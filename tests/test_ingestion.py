"""
Unit Tests for Document Ingestion & Clause Offset Provenance
"""

import pytest
from backend.services.ingestion import IngestionService


def test_file_validation():
    # Valid size and MIME
    assert IngestionService.validate_file("doc.pdf", b"12345", "application/pdf") is True

    # Invalid MIME type
    with pytest.raises(ValueError):
        IngestionService.validate_file("script.exe", b"12345", "application/x-msdownload")


def test_clause_segmentation_provenance():
    doc_text = """AGREEMENT
SECTION 1. TERMINATION
Either party may terminate with 30 days notice.

SECTION 2. CONFIDENTIALITY
Information must remain confidential for 5 years.
"""
    metadata, clauses = IngestionService.parse_document(
        filename="test.txt",
        content_text=doc_text,
        mime_type="text/plain",
        tenant_id="tenant_test"
    )

    assert metadata.clause_count == 2
    assert clauses[0].section.startswith("SECTION 1")
    assert clauses[0].char_start >= 0
    assert clauses[0].char_end > clauses[0].char_start
    assert "30 days notice" in clauses[0].text
    assert clauses[1].section.startswith("SECTION 2")
