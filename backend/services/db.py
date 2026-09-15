"""
SQLite Persistent Storage Service for Documents, Clauses, and Audit Logs
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from backend.schemas.eglr import DocumentMetadata, ClauseObject

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "lawpedia.db"


def init_db():
    """
    Initializes SQLite schema for persistent storage of documents, clauses, and audit logs.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        title TEXT NOT NULL,
        metadata_json TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clauses (
        clause_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        clause_json TEXT NOT NULL,
        FOREIGN KEY(document_id) REFERENCES documents(document_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        user_id TEXT NOT NULL,
        tenant_id TEXT NOT NULL,
        details_json TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_document_persistent(metadata: DocumentMetadata, clauses: list[ClauseObject]):
    """
    Persists document metadata and clauses to SQLite disk database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO documents (document_id, tenant_id, filename, title, metadata_json) VALUES (?, ?, ?, ?, ?)",
        (metadata.document_id, metadata.tenant_id, metadata.filename, metadata.title, metadata.model_dump_json())
    )

    for c in clauses:
        cursor.execute(
            "INSERT OR REPLACE INTO clauses (clause_id, document_id, tenant_id, clause_json) VALUES (?, ?, ?, ?)",
            (c.clause_id, metadata.document_id, metadata.tenant_id, c.model_dump_json())
        )

    conn.commit()
    conn.close()


def load_persistent_documents(tenant_id: Optional[str] = None) -> list[DocumentMetadata]:
    """
    Loads persisted documents from SQLite database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if tenant_id:
        cursor.execute("SELECT metadata_json FROM documents WHERE tenant_id = ?", (tenant_id,))
    else:
        cursor.execute("SELECT metadata_json FROM documents")

    rows = cursor.fetchall()
    conn.close()

    docs = []
    for r in rows:
        docs.append(DocumentMetadata.model_validate_json(r[0]))
    return docs


def load_persistent_clauses(document_id: str) -> list[ClauseObject]:
    """
    Loads persisted clauses for a document from SQLite database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT clause_json FROM clauses WHERE document_id = ?", (document_id,))
    rows = cursor.fetchall()
    conn.close()

    clauses = []
    for r in rows:
        clauses.append(ClauseObject.model_validate_json(r[0]))
    return clauses


def load_all_persistent_data() -> list[tuple[DocumentMetadata, list[ClauseObject]]]:
    """
    Loads all persisted documents and clauses from SQLite.
    """
    docs = load_persistent_documents()
    res = []
    for d in docs:
        clauses = load_persistent_clauses(d.document_id)
        res.append((d, clauses))
    return res
