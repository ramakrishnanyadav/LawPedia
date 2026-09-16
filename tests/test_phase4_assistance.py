"""
Unit tests for Phase 4 Legal Assistance Value Enhancements:
1. Citation references on EvidenceSpans
2. Jurisdiction-awareness & statutory override caveats
3. Plain-English checklist generation (/checklist endpoint)
4. Side-by-side clause comparison diff deltas
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.eglr import DocumentMetadata, ClauseObject, EvidenceSpan
from backend.services.retrieval import HybridRetrievalService
from backend.services.comparison import ComparisonService
from backend.services.handoff import LawyerHandoffService

client = TestClient(app)


def test_evidence_span_citation_formatting():
    service = HybridRetrievalService()
    meta = DocumentMetadata(
        document_id="doc_cit_1",
        filename="Contract_Citation_Test.pdf",
        title="Citation Agreement",
        mime_type="application/pdf",
        page_count=5,
        clause_count=1,
        jurisdiction="California",
        tenant_id="tenant_cit_test",
        upload_timestamp="2026-09-16T00:00:00Z"
    )
    clause = ClauseObject(
        clause_id="clause_cit_1",
        document_id="doc_cit_1",
        section="4.2",
        title="Payment Term",
        text="Payment shall be Net 30 days.",
        page=3,
        char_start=0,
        char_end=30
    )
    service.index_document(meta, [clause])
    spans = service.search("Payment terms", tenant_id="tenant_cit_test")

    assert len(spans) > 0
    span = spans[0]
    assert span.citation == "Section 4.2, page 3"


def test_comparison_side_by_side_delta():
    meta_a = DocumentMetadata(
        document_id="doc_cmp_a",
        filename="Master_v1.pdf",
        title="Master v1",
        mime_type="application/pdf",
        page_count=2,
        clause_count=1,
        tenant_id="tenant_cmp",
        upload_timestamp="2026-09-16T00:00:00Z"
    )
    clauses_a = [
        ClauseObject(
            clause_id="c_a_1",
            document_id="doc_cmp_a",
            section="Section 8",
            title="Liability Cap",
            text="Total liability is limited to $100,000.",
            page=1,
            char_start=0,
            char_end=40
        )
    ]

    meta_b = DocumentMetadata(
        document_id="doc_cmp_b",
        filename="Master_v2.pdf",
        title="Master v2",
        mime_type="application/pdf",
        page_count=2,
        clause_count=1,
        tenant_id="tenant_cmp",
        upload_timestamp="2026-09-16T00:00:00Z"
    )
    clauses_b = [
        ClauseObject(
            clause_id="c_b_1",
            document_id="doc_cmp_b",
            section="Section 8",
            title="Liability Cap",
            text="Total liability is unlimited for all breaches.",
            page=1,
            char_start=0,
            char_end=45
        )
    ]

    result = ComparisonService.compare_documents(meta_a, clauses_a, meta_b, clauses_b)
    liability_item = next(i for i in result.items if i.dimension == "Liability Cap")
    assert liability_item.side_by_side_delta is not None
    assert "[- Master_v1.pdf:" in liability_item.side_by_side_delta
    assert "{+ Master_v2.pdf:" in liability_item.side_by_side_delta


def test_plain_english_checklist_service():
    """
    Verifies that the plain-English checklist derives content from actual uploaded clauses,
    not from hardcoded fabricated section references. A regression back to hardcoded output
    should cause this test to fail.
    """
    meta = DocumentMetadata(
        document_id="doc_chk_1",
        filename="SLA_Agreement.pdf",
        title="SLA Agreement",
        mime_type="application/pdf",
        page_count=3,
        clause_count=2,
        tenant_id="tenant_chk",
        upload_timestamp="2026-09-16T00:00:00Z"
    )
    from backend.schemas.eglr import Obligation, RiskLevel

    high_risk_clause = ClauseObject(
        clause_id="c_chk_high",
        document_id="doc_chk_1",
        section="Section 7",
        title="Unlimited Liability Exposure",
        text="Vendor shall be liable for all damages, direct and indirect, without limit.",
        page=2,
        char_start=0,
        char_end=80,
        risk_level=RiskLevel.CRITICAL,
        obligations=[
            Obligation(
                party="Vendor",
                obligation_text="Vendor must cover all damages without cap.",
                clause_id="c_chk_high"
            )
        ]
    )
    low_risk_clause = ClauseObject(
        clause_id="c_chk_low",
        document_id="doc_chk_1",
        section="Section 4",
        title="Notice",
        text="Notice of 90 days required.",
        page=1,
        char_start=0,
        char_end=30,
        risk_level=RiskLevel.LOW
    )

    checklist = LawyerHandoffService.generate_plain_english_checklist([meta], [high_risk_clause, low_risk_clause])

    # Must have content
    assert len(checklist.things_to_negotiate) >= 1
    assert len(checklist.dates_not_to_miss) >= 1
    assert len(checklist.risk_red_flags) >= 1

    # Content must be grounded in actual clause text — NOT fabricated static references
    negotiate_refs = [item.clause_reference for item in checklist.things_to_negotiate if item.clause_reference]
    red_flag_refs = [item.clause_reference for item in checklist.risk_red_flags if item.clause_reference]

    # The real clause is Section 7 page 2 — must appear, not "Section 8" or "Section 14.1"
    assert any("Section 7" in ref for ref in negotiate_refs + red_flag_refs), \
        "Checklist must reference actual clause section (Section 7), not hardcoded fabricated sections"
    assert not any("Section 8" in ref or "Section 14.1" in ref or "Section 6.2" in ref
                   for ref in negotiate_refs + red_flag_refs), \
        "Checklist must not contain hardcoded fabricated section references"

    # Description must trace back to actual clause obligation text
    negotiate_descriptions = [item.description for item in checklist.things_to_negotiate]
    assert any("Vendor" in desc or "damages" in desc.lower() for desc in negotiate_descriptions), \
        "Negotiate item must reference real obligation text from the clause"


def test_plain_english_checklist_empty_state():
    """
    Verifies that an empty, honest checklist is returned when document has no risk clauses —
    not fabricated placeholder content.
    """
    meta = DocumentMetadata(
        document_id="doc_empty_1",
        filename="Simple_Agreement.pdf",
        title="Simple Agreement",
        mime_type="application/pdf",
        page_count=1,
        clause_count=1,
        tenant_id="tenant_empty",
        upload_timestamp="2026-09-16T00:00:00Z"
    )
    low_clause = ClauseObject(
        clause_id="c_empty_1",
        document_id="doc_empty_1",
        section="Section 1",
        title="Scope",
        text="Parties agree to cooperate.",
        page=1,
        char_start=0,
        char_end=30
    )
    checklist = LawyerHandoffService.generate_plain_english_checklist([meta], [low_clause])

    # Empty state must be honest — no fabricated content
    assert len(checklist.things_to_negotiate) == 1
    assert "No high-risk" in checklist.things_to_negotiate[0].title
    assert len(checklist.risk_red_flags) == 1
    assert "No critical" in checklist.risk_red_flags[0].title
    assert len(checklist.dates_not_to_miss) == 1
    assert "No key dates" in checklist.dates_not_to_miss[0].title


def test_checklist_api_endpoint(monkeypatch):
    from backend.config import settings
    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_MODE", True)
    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_TOKEN", "lawpedia_demo_token_2026")

    response = client.post(
        "/api/checklist",
        headers={"Authorization": "Bearer lawpedia_demo_token_2026"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "things_to_negotiate" in data
    assert "dates_not_to_miss" in data
    assert "risk_red_flags" in data
