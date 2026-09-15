"""
Evidence-Governed Legal Reasoning (EGLR) Pydantic Schema Contracts
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class SupportStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceSpan(BaseModel):
    source_document_id: str = Field(..., description="Unique ID of the source legal document")
    document_name: str = Field(..., description="Human-readable filename")
    page: int = Field(default=1, description="Page number where evidence originates")
    section: str = Field(default="General", description="Section title in document")
    clause_id: str = Field(..., description="Unique identifier of clause")
    evidence_span: str = Field(..., description="Exact textual excerpt from document")
    document_version: str = Field(default="v1.0", description="Document version string")
    effective_date: Optional[str] = Field(default=None, description="Effective date ISO format")
    jurisdiction: Optional[str] = Field(default="General", description="Governing jurisdiction")
    retrieval_confidence: float = Field(default=0.95, description="Confidence score 0.0-1.0")


class ClaimVerification(BaseModel):
    claim_id: str = Field(..., description="Unique ID of the generated claim")
    claim: str = Field(..., description="Factual legal assertion made")
    evidence: Optional[EvidenceSpan] = Field(default=None, description="Primary supporting evidence span")
    support_status: SupportStatus = Field(default=SupportStatus.SUPPORTED)
    verification_notes: Optional[str] = Field(default=None, description="Reasoning behind support status")


class Obligation(BaseModel):
    party: str
    obligation_text: str
    clause_id: str
    conditional_on: Optional[str] = None
    deadline: Optional[str] = None
    penalty: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


class ClauseObject(BaseModel):
    clause_id: str
    document_id: str
    section: str
    title: str
    text: str
    page: int
    char_start: int
    char_end: int
    entities: list[str] = Field(default_factory=list)
    obligations: list[Obligation] = Field(default_factory=list)
    rights: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    superseded_by: Optional[str] = None


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    title: str
    mime_type: str
    page_count: int
    clause_count: int
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    jurisdiction: str = "General"
    parties: list[str] = Field(default_factory=list)
    document_version: str = "v1.0"
    tenant_id: str = "tenant_lawpedia_demo"
    upload_timestamp: str


class ComparisonItem(BaseModel):
    dimension: str  # e.g., "Termination Notice", "Liability Cap"
    status: str     # "UNCHANGED", "MODIFIED", "ADDED", "REMOVED", "CONFLICTING"
    doc_a_clause: Optional[str] = None
    doc_b_clause: Optional[str] = None
    doc_a_text: Optional[str] = None
    doc_b_text: Optional[str] = None
    analysis: str
    risk_impact: RiskLevel = RiskLevel.LOW


class ComparisonResult(BaseModel):
    doc_a_id: str
    doc_b_id: str
    doc_a_name: str
    doc_b_name: str
    summary: str
    items: list[ComparisonItem] = Field(default_factory=list)


class LawyerHandoffPack(BaseModel):
    handoff_id: str
    generated_at: str
    matter_summary: str
    parties_involved: list[str]
    relevant_documents: list[str]
    key_clauses: list[dict[str, str]]
    key_obligations: list[Obligation]
    important_dates: list[dict[str, str]]
    potential_conflicts: list[str]
    unanswered_questions: list[str]
    evidence_references: list[EvidenceSpan]
    questions_for_lawyer: list[str]


class FalsePremiseCheck(BaseModel):
    has_false_premise: bool
    detected_premise: Optional[str] = None
    correction: Optional[str] = None
    evidence: Optional[EvidenceSpan] = None


class AskQueryRequest(BaseModel):
    query: str
    document_ids: Optional[list[str]] = None
    tenant_id: str = "tenant_lawpedia_demo"


class AskQueryResponse(BaseModel):
    query: str
    plain_language_answer: str
    claims: list[ClaimVerification]
    support_status: SupportStatus
    false_premise_check: FalsePremiseCheck
    important_conditions: list[str]
    conflicts_or_uncertainty: list[str]
    practical_next_steps: list[str]
    questions_to_ask_lawyer: list[str]
    evidence_spans: list[EvidenceSpan]
    legal_disclaimer: str


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    clause_count: int
    metadata: DocumentMetadata
