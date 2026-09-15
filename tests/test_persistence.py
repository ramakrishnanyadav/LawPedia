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
