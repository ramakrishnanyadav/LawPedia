"""
Lawpedia FastAPI Router Endpoints
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from backend.schemas.eglr import (
    AskQueryRequest, AskQueryResponse, DocumentUploadResponse,
    ComparisonResult, LawyerHandoffPack, SupportStatus, ClaimVerification, FalsePremiseCheck,
    PlainEnglishChecklist
)
from backend.services.ingestion import IngestionService
from backend.services.extraction import LegalExtractionService
from backend.services.retrieval import HybridRetrievalService
from backend.services.graph import LegalEvidenceGraph
from backend.services.comparison import ComparisonService
from backend.services.false_premise import FalsePremiseDetector
from backend.services.verification import ClaimVerificationEngine
from backend.services.handoff import LawyerHandoffService
from backend.services.safety import SafetyGateway
from backend.services.audit import log_audit_event, get_audit_logs
from backend.api.metrics_routes import metrics_router

from backend.services.auth import verify_firebase_token, AuthenticatedUser
from backend.services.simplification import LegalSimplificationService
from backend.services.retrieval import get_embedding_backend_type
from backend.services.db import save_document_persistent, load_persistent_documents, load_all_persistent_data

router = APIRouter()
router.include_router(metrics_router)

# Global state instances for single-instance app
retrieval_service = HybridRetrievalService()
evidence_graph = LegalEvidenceGraph()
documents_store = {}
clauses_store = {}


def reload_stores_from_db():
    """
    Reloads persisted documents and clauses from SQLite into memory indexes.
    """
    for meta, clauses in load_all_persistent_data():
        documents_store[meta.document_id] = meta
        clauses_store[meta.document_id] = clauses
        retrieval_service.index_document(meta, clauses)
        evidence_graph.add_document_subgraph(meta, clauses)


# Initialize memory stores from SQLite persistence on module import
reload_stores_from_db()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Lawpedia Legal Intelligence Platform API",
        "version": "2.0.0",
        "embedding_backend": get_embedding_backend_type()
    }


@router.post("/upload", response_model=DocumentUploadResponse, responses={400: {"description": "Bad Request"}, 500: {"description": "Internal Server Error"}})
async def upload_document(
    file: Optional[UploadFile] = File(None),
    filename: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None),
    document_version: Optional[str] = Form("v1.0"),
    user: AuthenticatedUser = Depends(verify_firebase_token)
):
    """
    Ingests a legal document file or raw text, redacts sensitive PII, extracts clauses and entities,
    indexes into hybrid vector search and Legal Evidence Graph, and logs audit event.
    Derived tenant_id strictly from verified server-side authentication token.
    """
    try:
        tenant_id = user.tenant_id
        fname = file.filename if file else (filename or "Document.txt")
        content = ""
        mime = "text/plain"

        if file:
            file_bytes = await file.read()
            mime = file.content_type or "text/plain"
            IngestionService.validate_file(fname, file_bytes, mime)
            content = file_bytes.decode("utf-8", errors="ignore")
        elif text_content:
            content = text_content
        else:
            raise HTTPException(status_code=400, detail="Must provide either file upload or text_content")

        # 1. Live PII Redaction on upload
        content = SafetyGateway.redact_pii(content)

        # 2. Sanitize prompt-injection data boundary
        content = SafetyGateway.sanitize_prompt_evidence(content)

        # Parse document into clauses
        metadata, clauses = IngestionService.parse_document(
            filename=fname,
            content_text=content,
            mime_type=mime,
            tenant_id=tenant_id,
            custom_version=document_version
        )

        # Extract obligations & rights for each clause
        for clause in clauses:
            clause.obligations = LegalExtractionService.extract_obligations(clause)
            clause.rights = LegalExtractionService.extract_rights(clause)

        # Index in retrieval and graph
        retrieval_service.index_document(metadata, clauses)
        evidence_graph.add_document_subgraph(metadata, clauses)

        # Store in-memory and persist to SQLite disk database
        documents_store[metadata.document_id] = metadata
        clauses_store[metadata.document_id] = clauses
        save_document_persistent(metadata, clauses)

        log_audit_event(
            event_type="DOCUMENT_UPLOAD",
            user_id=user.uid,
            tenant_id=tenant_id,
            details={"document_id": metadata.document_id, "filename": fname, "clause_count": len(clauses)}
        )

        return DocumentUploadResponse(
            document_id=metadata.document_id,
            filename=metadata.filename,
            status="SUCCESS",
            clause_count=len(clauses),
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
def list_documents(user: AuthenticatedUser = Depends(verify_firebase_token)):
    """
    Lists uploaded documents filtered strictly by verified tenant isolation.
    """
    docs = [meta for meta in documents_store.values() if meta.tenant_id == user.tenant_id]
    return {"documents": docs}


@router.post("/query", response_model=AskQueryResponse)
def ask_question(
    request: AskQueryRequest,
    user: AuthenticatedUser = Depends(verify_firebase_token)
):
    """
    Executes Evidence-Governed Legal Query answering with server-derived tenant isolation:
    1. Hybrid Retrieval (BM25 + Dense Vector + Metadata Filtering)
    2. False Premise Detection
    3. Claim-Level Verification
    4. Plain-Language Simplification
    5. Explicit Abstention if evidence is missing
    6. Legal Safety Disclaimer
    """
    tenant_id = user.tenant_id

    log_audit_event(
        event_type="LEGAL_QUERY",
        user_id=user.uid,
        tenant_id=tenant_id,
        details={"query": request.query, "document_ids": request.document_ids}
    )

    # 1. Retrieve evidence spans
    spans = retrieval_service.search(
        query=request.query,
        tenant_id=tenant_id,
        target_document_ids=request.document_ids,
        top_k=5
    )

    # Check for mandatory abstention
    top_confidence = spans[0].retrieval_confidence if spans else 0.0
    should_abstain, abstain_reason = SafetyGateway.should_abstain(top_confidence, len(spans))

    if should_abstain:
        return AskQueryResponse(
            query=request.query,
            plain_language_answer=f"ABSTENTION: Lawpedia cannot provide a grounded answer for this query. Reason: {abstain_reason}",
            claims=[
                ClaimVerification(
                    claim_id="CLAIM_001",
                    claim="Insufficient legal evidence in library.",
                    evidence=None,
                    support_status=SupportStatus.INSUFFICIENT_EVIDENCE,
                    verification_notes=abstain_reason
                )
            ],
            support_status=SupportStatus.INSUFFICIENT_EVIDENCE,
            false_premise_check=FalsePremiseCheck(has_false_premise=False),
            important_conditions=["Ensure all relevant contracts and amendments are uploaded to the document library."],
            conflicts_or_uncertainty=["Zero matching evidence spans found for the requested topic."],
            practical_next_steps=["Upload the governing document or amendment PDF to enable grounded retrieval."],
            questions_to_ask_lawyer=["Where can the primary copy of this agreement be obtained?"],
            evidence_spans=[],
            legal_disclaimer=SafetyGateway.MANDATORY_LEGAL_DISCLAIMER
        )

    # 2. Check for False Premises
    fp_check = FalsePremiseDetector.inspect_query_premises(request.query, spans)

    # 3. Generate plain language grounded simplification
    primary_span = spans[0]
    simplified_text = LegalSimplificationService.simplify_evidence_spans(spans[:2], reading_level="simple")

    plain_answer = ""
    if fp_check.has_false_premise:
        plain_answer = f"{fp_check.correction}\n\n{simplified_text}"
    else:
        plain_answer = f"PLAIN LANGUAGE EXPLANATION:\n{simplified_text}"

    raw_claims = [
        f"The terms of {primary_span.document_name} apply under {primary_span.jurisdiction} jurisdiction.",
        f"Relevant clause excerpt: '{primary_span.evidence_span[:120]}...'"
    ]

    verified_claims = ClaimVerificationEngine.verify_claims(raw_claims, spans)

    overall_status = SupportStatus.SUPPORTED if all(c.support_status == SupportStatus.SUPPORTED for c in verified_claims) else SupportStatus.PARTIALLY_SUPPORTED
    jurisdiction = primary_span.jurisdiction or "General"
    statutory_caveat = f"Note: This analysis does not account for {jurisdiction}-specific statutory overrides or mandatory local regulations."

    return AskQueryResponse(
        query=request.query,
        plain_language_answer=plain_answer,
        claims=verified_claims,
        support_status=overall_status,
        false_premise_check=fp_check,
        important_conditions=[
            "Terms subject to active effective dates and governing jurisdiction.",
            statutory_caveat
        ],
        conflicts_or_uncertainty=["Verify if any subsequent side-letter or amendment modifies these terms."],
        practical_next_steps=["Review full clause excerpt in Clause Explorer.", "Export Lawyer Handoff Pack for counsel review."],
        questions_to_ask_lawyer=[f"Does this specific provision meet statutory compliance requirements in {jurisdiction}?"],
        evidence_spans=spans,
        legal_disclaimer=SafetyGateway.MANDATORY_LEGAL_DISCLAIMER
    )


@router.post("/compare", response_model=ComparisonResult, responses={403: {"description": "Access Denied"}, 404: {"description": "Document Not Found"}})
def compare_documents(
    doc_a_id: str,
    doc_b_id: str,
    user: AuthenticatedUser = Depends(verify_firebase_token)
):
    """
    Compares two contracts semantically across 10 legal dimensions.
    """
    meta_a = documents_store.get(doc_a_id)
    clauses_a = clauses_store.get(doc_a_id)
    meta_b = documents_store.get(doc_b_id)
    clauses_b = clauses_store.get(doc_b_id)

    if not meta_a or not meta_b:
        raise HTTPException(status_code=404, detail="One or both requested documents were not found")

    if meta_a.tenant_id != user.tenant_id or meta_b.tenant_id != user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied: Documents belong to another tenant.")

    return ComparisonService.compare_documents(meta_a, clauses_a, meta_b, clauses_b)


@router.get("/graph")
def get_graph(user: AuthenticatedUser = Depends(verify_firebase_token)):
    """
    Exports the visual and tabular Legal Evidence Graph filtered by tenant_id.
    """
    return evidence_graph.get_exportable_graph(tenant_id=user.tenant_id)


@router.post("/handoff", response_model=LawyerHandoffPack)
def generate_handoff(user: AuthenticatedUser = Depends(verify_firebase_token)):
    """
    Generates the 10-section Lawyer Handoff Pack for authenticated tenant.
    """
    tenant_id = user.tenant_id
    tenant_docs = [meta for meta in documents_store.values() if meta.tenant_id == tenant_id]
    tenant_clauses = []
    for d in tenant_docs:
        tenant_clauses.extend(clauses_store.get(d.document_id, []))

    spans = retrieval_service.search(query="all clauses obligations", tenant_id=tenant_id, top_k=10)
    return LawyerHandoffService.generate_handoff_pack(tenant_docs, tenant_clauses, spans)


@router.api_route("/checklist", methods=["GET", "POST"], response_model=PlainEnglishChecklist)
def generate_checklist(user: AuthenticatedUser = Depends(verify_firebase_token)):
    """
    Generates plain-English actionable checklist (things to negotiate, dates not to miss, risk red flags).
    """
    tenant_id = user.tenant_id
    tenant_docs = [meta for meta in documents_store.values() if meta.tenant_id == tenant_id]
    tenant_clauses = []
    for d in tenant_docs:
        tenant_clauses.extend(clauses_store.get(d.document_id, []))

    return LawyerHandoffService.generate_plain_english_checklist(tenant_docs, tenant_clauses)


@router.get("/audit")
def get_audit(user: AuthenticatedUser = Depends(verify_firebase_token)):
    """
    Returns audit logs for verified tenant isolation.
    """
    return {"audit_logs": get_audit_logs(user.tenant_id)}


