"""
SQLite Persistent Storage Service for Documents, Clauses, and Audit Logs
"""

import sqlite3
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from backend.schemas.eglr import DocumentMetadata, ClauseObject

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "lawpedia.db"

_conn_lock = threading.Lock()
_connection: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.execute("PRAGMA journal_mode=WAL")
        _init_db_schema(_connection)
    return _connection


def _init_db_schema(conn: sqlite3.Connection):
    with _conn_lock:
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
            embedding_json TEXT,
            tokens_json TEXT,
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

        # Migration: Add embedding_json and tokens_json to existing clauses table if missing
        try:
            cursor.execute("ALTER TABLE clauses ADD COLUMN embedding_json TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE clauses ADD COLUMN tokens_json TEXT")
        except sqlite3.OperationalError:
            pass

        # Indexes for tenant-scoped & document-scoped queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_document ON clauses(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_tenant ON clauses(tenant_id)")

        conn.commit()


def init_db():
    """
    Public entry point for initializing database schema.
    """
    get_connection()


def save_document_persistent(
    metadata: DocumentMetadata,
    clauses: list[ClauseObject],
    embedding_cache: Optional[dict[str, list[float]]] = None,
    tokenized_cache: Optional[dict[str, list[str]]] = None
):
    """
    Persists document metadata, clauses, embeddings, and token lists to SQLite disk database
    using executemany batch insertion and the shared connection.
    """
    conn = get_connection()
    with _conn_lock:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO documents (document_id, tenant_id, filename, title, metadata_json) VALUES (?, ?, ?, ?, ?)",
            (metadata.document_id, metadata.tenant_id, metadata.filename, metadata.title, metadata.model_dump_json())
        )

        clause_rows = []
        for c in clauses:
            emb = embedding_cache.get(c.clause_id) if embedding_cache else None
            toks = tokenized_cache.get(c.clause_id) if tokenized_cache else None
            clause_rows.append((
                c.clause_id,
                metadata.document_id,
                metadata.tenant_id,
                c.model_dump_json(),
                json.dumps(emb) if emb else None,
                json.dumps(toks) if toks else None
            ))

        if clause_rows:
            cursor.executemany(
                "INSERT OR REPLACE INTO clauses (clause_id, document_id, tenant_id, clause_json, embedding_json, tokens_json) VALUES (?, ?, ?, ?, ?, ?)",
                clause_rows
            )

        conn.commit()


def load_persistent_documents(tenant_id: Optional[str] = None) -> list[DocumentMetadata]:
    """
    Loads persisted documents from SQLite database using tenant index when filtered.
    """
    conn = get_connection()
    with _conn_lock:
        cursor = conn.cursor()
        if tenant_id:
            cursor.execute("SELECT metadata_json FROM documents WHERE tenant_id = ?", (tenant_id,))
        else:
            cursor.execute("SELECT metadata_json FROM documents")
        rows = cursor.fetchall()

    return [DocumentMetadata.model_validate_json(r[0]) for r in rows]


def load_persistent_clauses(document_id: str) -> list[ClauseObject]:
    """
    Loads persisted clauses for a document from SQLite database.
    """
    conn = get_connection()
    with _conn_lock:
        cursor = conn.cursor()
        cursor.execute("SELECT clause_json FROM clauses WHERE document_id = ?", (document_id,))
        rows = cursor.fetchall()

    return [ClauseObject.model_validate_json(r[0]) for r in rows]


def load_all_persistent_data() -> list[tuple[DocumentMetadata, list[ClauseObject], dict[str, list[float]], dict[str, list[str]]]]:
    """
    Loads all persisted documents, clauses, embeddings, and tokens in 2 batch queries total (0 N+1 overhead).
    """
    conn = get_connection()
    with _conn_lock:
        docs_rows = conn.execute("SELECT document_id, metadata_json FROM documents").fetchall()
        clause_rows = conn.execute("SELECT document_id, clause_id, clause_json, embedding_json, tokens_json FROM clauses").fetchall()

    clauses_by_doc: dict[str, list[ClauseObject]] = {}
    embeddings_by_doc: dict[str, dict[str, list[float]]] = {}
    tokens_by_doc: dict[str, dict[str, list[str]]] = {}

    for doc_id, clause_id, clause_json, emb_json, tok_json in clause_rows:
        c = ClauseObject.model_validate_json(clause_json)
        clauses_by_doc.setdefault(doc_id, []).append(c)
        if emb_json:
            embeddings_by_doc.setdefault(doc_id, {})[clause_id] = json.loads(emb_json)
        if tok_json:
            tokens_by_doc.setdefault(doc_id, {})[clause_id] = json.loads(tok_json)

    result = []
    for doc_id, metadata_json in docs_rows:
        meta = DocumentMetadata.model_validate_json(metadata_json)
        result.append((
            meta,
            clauses_by_doc.get(doc_id, []),
            embeddings_by_doc.get(doc_id, {}),
            tokens_by_doc.get(doc_id, {})
        ))
    return result
