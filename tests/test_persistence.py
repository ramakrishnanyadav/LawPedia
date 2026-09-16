"""
SQLite Document & Clause Persistence Test Suite
"""

import pytest
from backend.services.ingestion import IngestionService
from backend.services.db import save_document_persistent, load_persistent_documents, load_persistent_clauses


def test_sqlite_document_persistence():
    meta, clauses = IngestionService.parse_document(
        filename="Persist_Test_Doc.txt",
        content_text="SECTION 1. OBLIGATIONS\nVendor must deliver monthly audit report.",
        tenant_id="tenant_sqlite_test"
    )

    # Save to SQLite database
    save_document_persistent(meta, clauses)

    # Re-query SQLite database directly
    loaded_docs = load_persistent_documents(tenant_id="tenant_sqlite_test")
    assert any(d.document_id == meta.document_id for d in loaded_docs)

    loaded_clauses = load_persistent_clauses(meta.document_id)
    assert len(loaded_clauses) == len(clauses)
    assert loaded_clauses[0].clause_id == clauses[0].clause_id


def test_sqlite_embedding_and_token_cache_persistence():
    from backend.services.retrieval import HybridRetrievalService
    from backend.services.db import load_all_persistent_data

    meta, clauses = IngestionService.parse_document(
        filename="Cache_Test_Doc.txt",
        content_text="SECTION 1. CONFIDENTIALITY\nReceiving party shall maintain secrecy for 5 years.",
        tenant_id="tenant_cache_test"
    )

    retrieval = HybridRetrievalService()
    retrieval.index_document(meta, clauses)

    # Save metadata, clauses, embeddings, and tokens to SQLite
    save_document_persistent(
        meta,
        clauses,
        embedding_cache=retrieval.embedding_cache,
        tokenized_cache=retrieval._tokenized_cache
    )

    # Load from DB in 2 batch queries
    all_data = load_all_persistent_data()
    match = [item for item in all_data if item[0].document_id == meta.document_id]
    assert len(match) == 1
    loaded_meta, loaded_clauses, loaded_embs, loaded_toks = match[0]

    assert len(loaded_clauses) == len(clauses)
    for c in clauses:
        assert c.clause_id in loaded_embs
        assert c.clause_id in loaded_toks

    # Create new clean retrieval service and populate from cache
    new_retrieval = HybridRetrievalService()
    new_retrieval.index_document_from_cache(loaded_meta, loaded_clauses, loaded_embs, loaded_toks)

    for c in clauses:
        assert c.clause_id in new_retrieval.embedding_cache
        assert c.clause_id in new_retrieval._tokenized_cache
        assert c.clause_id in new_retrieval._token_freq_cache

