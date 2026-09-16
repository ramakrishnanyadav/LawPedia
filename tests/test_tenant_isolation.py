"""
Automated Multi-Tenant Data Isolation Regression Test Suite
"""

import pytest
from backend.services.ingestion import IngestionService
from backend.services.retrieval import HybridRetrievalService
from backend.services.audit import log_audit_event, get_audit_logs
from backend.services.handoff import LawyerHandoffService


def test_strict_tenant_isolation_retrieval():
    retrieval = HybridRetrievalService()

    # Ingest document for Tenant Alpha
    meta_alpha, clauses_alpha = IngestionService.parse_document(
        filename="Alpha_Confidential_NDA.txt",
        content_text="SECTION 1. CONFIDENTIALITY\nAlpha secret project code is ALPHA-99.",
        tenant_id="tenant_ALPHA"
    )
    retrieval.index_document(meta_alpha, clauses_alpha)

    # Ingest document for Tenant Beta
    meta_beta, clauses_beta = IngestionService.parse_document(
        filename="Beta_Confidential_NDA.txt",
        content_text="SECTION 1. CONFIDENTIALITY\nBeta secret project code is BETA-88.",
        tenant_id="tenant_BETA"
    )
    retrieval.index_document(meta_beta, clauses_beta)

    # 1. Tenant Alpha searches -> must ONLY return Alpha documents
    spans_alpha = retrieval.search(query="secret project code", tenant_id="tenant_ALPHA")
    assert len(spans_alpha) == 1
    assert spans_alpha[0].source_document_id == meta_alpha.document_id
    assert "ALPHA-99" in spans_alpha[0].evidence_span
    assert "BETA-88" not in spans_alpha[0].evidence_span

    # 2. Tenant Beta searches -> must ONLY return Beta documents
    spans_beta = retrieval.search(query="secret project code", tenant_id="tenant_BETA")
    assert len(spans_beta) == 1
    assert spans_beta[0].source_document_id == meta_beta.document_id
    assert "BETA-88" in spans_beta[0].evidence_span
    assert "ALPHA-99" not in spans_beta[0].evidence_span

    # 3. Direct IDOR attempt: Tenant Alpha tries to query target_document_ids of Tenant Beta
    idor_spans = retrieval.search(
        query="secret project code",
        tenant_id="tenant_ALPHA",
        target_document_ids=[meta_beta.document_id]
    )
    assert len(idor_spans) == 0  # REJECTED CROSS-TENANT READ


def test_tenant_audit_log_isolation():
    log_audit_event("QUERY", "user_1", "tenant_ALPHA", {"q": "Alpha query"})
    log_audit_event("QUERY", "user_2", "tenant_BETA", {"q": "Beta query"})

    logs_alpha = get_audit_logs("tenant_ALPHA")
    for log in logs_alpha:
        assert log["tenant_id"] == "tenant_ALPHA"

    logs_beta = get_audit_logs("tenant_BETA")
    for log in logs_beta:
        assert log["tenant_id"] == "tenant_BETA"


def test_tenant_handoff_pack_isolation():
    meta_alpha, clauses_alpha = IngestionService.parse_document(
        filename="Alpha_Contract.txt",
        content_text="SECTION 1. TERMS\nAlpha obligation text.",
        tenant_id="tenant_ALPHA"
    )
    meta_beta, clauses_beta = IngestionService.parse_document(
        filename="Beta_Contract.txt",
        content_text="SECTION 1. TERMS\nBeta obligation text.",
        tenant_id="tenant_BETA"
    )

    pack_alpha = LawyerHandoffService.generate_handoff_pack([meta_alpha], clauses_alpha, [])
    assert "Alpha_Contract.txt" in pack_alpha.relevant_documents
    assert "Beta_Contract.txt" not in pack_alpha.relevant_documents


def test_unauthenticated_api_request_rejected_401(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.config import settings

    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_MODE", True)
    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_TOKEN", "lawpedia_demo_token_2026")

    client = TestClient(app)
    
    # 1. /api/documents without Authorization header -> MUST RETURN 401 UNAUTHORIZED
    res_docs = client.get("/api/documents")
    assert res_docs.status_code == 401
    
    # 2. /api/query without Authorization header -> MUST RETURN 401 UNAUTHORIZED
    res_query = client.post("/api/query", json={"query": "test query"})
    assert res_query.status_code == 401
    
    # 3. /api/handoff without Authorization header -> MUST RETURN 401 UNAUTHORIZED
    res_handoff = client.post("/api/handoff")
    assert res_handoff.status_code == 401

    # 4. Request with valid Bearer Token succeeds (200 OK)
    headers = {"Authorization": "Bearer lawpedia_demo_token_2026"}
    res_auth_docs = client.get("/api/documents", headers=headers)
    assert res_auth_docs.status_code == 200

    # 5. Request with garbage Bearer token MUST be rejected with 401 UNAUTHORIZED
    garbage_headers = {"Authorization": "Bearer aaaaaaaaaaaa"}
    res_garbage = client.get("/api/documents", headers=garbage_headers)
    assert res_garbage.status_code == 401


def test_graph_api_tenant_isolation(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.config import settings

    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_MODE", True)
    monkeypatch.setattr(settings, "LAWPEDIA_DEMO_TOKEN", "lawpedia_demo_token_2026")

    client = TestClient(app)
    headers = {"Authorization": "Bearer lawpedia_demo_token_2026"}

    # Upload document for demo tenant
    res_upload = client.post(
        "/api/upload",
        data={"text_content": "SECTION 1. CONFIDENTIALITY\nDemo secrecy clause.", "filename": "Demo_Doc.txt"},
        headers=headers
    )
    assert res_upload.status_code == 200

    # Fetch exportable graph
    res_graph = client.get("/api/graph", headers=headers)
    assert res_graph.status_code == 200
    graph_data = res_graph.json()
    assert "nodes" in graph_data
    assert "edges" in graph_data

    # Every returned node and edge must belong to tenant_lawpedia_demo
    for node in graph_data["nodes"]:
        assert node.get("tenant_id") == "tenant_lawpedia_demo"
    for edge in graph_data["edges"]:
        assert edge.get("tenant_id") == "tenant_lawpedia_demo"

