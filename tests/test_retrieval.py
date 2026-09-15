"""
Unit & Security Tests for Hybrid Retrieval & Tenant Isolation
"""

from backend.services.ingestion import IngestionService
from backend.services.retrieval import HybridRetrievalService


def test_tenant_isolation_retrieval():
    retrieval = HybridRetrievalService()

    meta_a, clauses_a = IngestionService.parse_document(
        filename="TenantA_NDA.txt",
        content_text="SECTION 1. CONFIDENTIALITY\nTenant A secret formula is X100.",
        tenant_id="tenant_A"
    )

    meta_b, clauses_b = IngestionService.parse_document(
        filename="TenantB_NDA.txt",
        content_text="SECTION 1. CONFIDENTIALITY\nTenant B secret formula is Y200.",
        tenant_id="tenant_B"
    )

    retrieval.index_document(meta_a, clauses_a)
    retrieval.index_document(meta_b, clauses_b)

    # Query as Tenant A
    results_a = retrieval.search(query="secret formula", tenant_id="tenant_A")
    assert len(results_a) == 1
    assert results_a[0].source_document_id == meta_a.document_id
    assert "Tenant A" in results_a[0].evidence_span

    # Query as Tenant B
    results_b = retrieval.search(query="secret formula", tenant_id="tenant_B")
    assert len(results_b) == 1
    assert results_b[0].source_document_id == meta_b.document_id
    assert "Tenant B" in results_b[0].evidence_span


def test_semantic_similarity_lexically_dissimilar():
    retrieval = HybridRetrievalService()
    v1 = retrieval._compute_semantic_embedding("Vendor shall maintain 99.9% uptime")
    v2 = retrieval._compute_semantic_embedding("The service provider must ensure the system is available almost all the time")
    v3 = retrieval._compute_semantic_embedding("Cheesecake recipes require sugar and eggs")
    
    sim_related = retrieval._cosine_similarity(v1, v2)
    sim_unrelated = retrieval._cosine_similarity(v1, v3)
    
    assert sim_related > 0.35, f"Expected high semantic similarity for related sentences, got {sim_related}"
    assert sim_related > sim_unrelated + 0.25, f"Related similarity ({sim_related}) must be significantly higher than unrelated ({sim_unrelated})"


