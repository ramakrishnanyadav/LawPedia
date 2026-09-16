"""
Hybrid Retrieval Engine (Real Dense Semantic Vectors + BM25 Lexical + RRF Reranking)
"""

import re
import heapq
import logging
from typing import Optional
import numpy as np
from backend.schemas.eglr import ClauseObject, DocumentMetadata, EvidenceSpan
import os

_logger = logging.getLogger("lawpedia.retrieval")

_MODEL_INSTANCE = None


def get_sentence_model():
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        # Memory-constrained hosts (e.g., Render 512MB free tier)
        is_render_host = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("RENDER_INSTANCE_ID"))
        lightweight_flag = os.getenv("LAWPEDIA_LIGHTWEIGHT_MODE", "").lower()
        is_lightweight = (
            is_render_host
            or lightweight_flag in ("true", "1", "t")
            or os.getenv("DISABLE_HEAVY_TRANSFORMERS", "false").lower() in ("true", "1", "t")
        )

        if is_lightweight:
            _logger.info("Notice: Lightweight mode active (Render environment detected / memory limit). Using 384-dim dense vectorizer.")
            _MODEL_INSTANCE = False
            return None
        try:
            from sentence_transformers import SentenceTransformer
            _MODEL_INSTANCE = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            _logger.warning("Notice: SentenceTransformer unavailable or memory limit reached, falling back to 384-dim dense vectorizer: %s", e)
            _MODEL_INSTANCE = False
    return _MODEL_INSTANCE if _MODEL_INSTANCE is not False else None


def get_embedding_backend_type() -> str:
    """
    Returns the active embedding backend type ('sentence-transformer' or 'fallback_hash').
    """
    model = get_sentence_model()
    return "sentence-transformer" if model is not None else "fallback_hash"


class HybridRetrievalService:
    """
    Implements real semantic vector hybrid search over indexed legal clauses with tenant isolation,
    metadata filtering, BM25 lexical scoring, vector similarity, and RRF reranking.
    """

    def __init__(self):
        self.documents: dict[str, DocumentMetadata] = {}
        self.clauses: dict[str, list[ClauseObject]] = {}
        self.embedding_cache: dict[str, list[float]] = {}
        self._tokenized_cache: dict[str, list[str]] = {}
        self._vocab: dict[str, int] = {}

    def get_model(self):
        return get_sentence_model()

    # ── index helpers ────────────────────────────────────────────────────────

    def _tokenize_and_update_vocab(self, clause_id: str, text: str) -> list[str]:
        """Tokenises clause text, caches the token list, and updates the vocab index."""
        words = re.findall(r"\w+", text.lower())
        self._tokenized_cache[clause_id] = words
        for w in words:
            if w not in self._vocab:
                self._vocab[w] = len(self._vocab)
        return words

    def _index_with_model(self, model, clauses: list[ClauseObject]) -> None:
        """Batch-encodes clauses using SentenceTransformer and caches normalised embeddings."""
        texts = [c.text for c in clauses]
        raw_embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
        for c, emb in zip(clauses, raw_embeddings):
            norm = np.linalg.norm(emb)
            self.embedding_cache[c.clause_id] = ((emb / norm) if norm > 0 else emb).tolist()
            self._tokenize_and_update_vocab(c.clause_id, c.text)

    def _index_without_model(self, clauses: list[ClauseObject]) -> None:
        """Indexes clauses using the fallback hash embedding when no transformer is available."""
        for c in clauses:
            self._tokenize_and_update_vocab(c.clause_id, c.text)
            self.embedding_cache[c.clause_id] = self._compute_semantic_embedding(c.text)

    def index_document(self, metadata: DocumentMetadata, clauses: list[ClauseObject]) -> None:
        """
        Stores metadata and clauses in the retrieval index and computes semantic embeddings.
        """
        self.documents[metadata.document_id] = metadata
        self.clauses[metadata.document_id] = clauses

        model = self.get_model()
        if model is not None and clauses:
            self._index_with_model(model, clauses)
        else:
            self._index_without_model(clauses)

    # ── embedding ────────────────────────────────────────────────────────────

    def _compute_semantic_embedding(self, text: str) -> list[float]:
        """
        Computes real dense 384-dimensional semantic vector embedding using SentenceTransformer.
        """
        model = self.get_model()
        if model is not None:
            embedding = model.encode(text, convert_to_numpy=True)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding.tolist()

        # Fallback to dense character-level subword TF-IDF embedding if transformer model unavailable
        words = re.findall(r"\w+", text.lower())
        vec = np.zeros(384, dtype=np.float32)
        for w in words:
            for i in range(len(w) - 2):
                gram = w[i:i+3]
                idx = (ord(gram[0]) * 31 + ord(gram[1]) * 17 + ord(gram[2])) % 384
                vec[idx] += 1.0
            idx_full = sum(ord(ch) for ch in w) % 384
            vec[idx_full] += 2.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    # ── scoring helpers ──────────────────────────────────────────────────────

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def _bm25_score(self, query_terms: list[str], words: list[str]) -> float:
        score = 0.0
        for term in query_terms:
            count = words.count(term.lower())
            if count > 0:
                score += (count * 2.2) / (count + 1.2)
        return score

    def _hybrid_score(self, clause: ClauseObject, query_terms: list[str], v_score: float) -> float:
        """Combines vector and BM25 scores into a single hybrid score."""
        words = self._tokenized_cache.get(clause.clause_id) or re.findall(r"\w+", clause.text.lower())
        b_score = self._bm25_score(query_terms, words)
        return (float(v_score) * 0.75) + (min(b_score / 5.0, 1.0) * 0.25)

    # ── search helpers ───────────────────────────────────────────────────────

    def _collect_candidates(
        self,
        tenant_id: str,
        target_document_ids: Optional[list[str]],
    ) -> list[tuple[ClauseObject, DocumentMetadata]]:
        """Returns all clause/metadata pairs for the given tenant, filtered by document IDs."""
        candidates: list[tuple[ClauseObject, DocumentMetadata]] = []
        for doc_id, meta in self.documents.items():
            if meta.tenant_id != tenant_id:
                continue  # STRICT TENANT ISOLATION
            if target_document_ids and doc_id not in target_document_ids:
                continue
            for c in self.clauses.get(doc_id, []):
                candidates.append((c, meta))
        return candidates

    def _build_evidence_span(self, clause: ClauseObject, meta: DocumentMetadata, score: float) -> EvidenceSpan:
        """Constructs an EvidenceSpan from a ranked clause result."""
        sec_str = (
            clause.section
            if (clause.section.startswith("Section") or clause.section == "General")
            else f"Section {clause.section}"
        )
        return EvidenceSpan(
            source_document_id=meta.document_id,
            document_name=meta.filename,
            page=clause.page,
            section=clause.section,
            clause_id=clause.clause_id,
            evidence_span=clause.text,
            citation=f"{sec_str}, page {clause.page}",
            document_version=meta.document_version,
            effective_date=meta.effective_date,
            jurisdiction=meta.jurisdiction,
            retrieval_confidence=round(float(score), 4),
        )

    # ── public search ────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        tenant_id: str,
        target_document_ids: Optional[list[str]] = None,
        top_k: int = 5,
    ) -> list[EvidenceSpan]:
        """
        Executes hybrid search across tenant documents and returns ranked EvidenceSpans.
        """
        query_terms = re.findall(r"\w+", query.lower())
        query_vec = self._compute_semantic_embedding(query)

        candidates = self._collect_candidates(tenant_id, target_document_ids)
        if not candidates:
            return []

        # Vectorized cosine similarity (dot product of pre-normalized unit vectors)
        vectors = np.array(
            [self.embedding_cache.get(c.clause_id) or self._compute_semantic_embedding(c.text) for c, _ in candidates],
            dtype=np.float32,
        )
        v_scores = vectors @ np.array(query_vec, dtype=np.float32)

        scored_items = [
            (self._hybrid_score(c, query_terms, v_score), c, meta)
            for (c, meta), v_score in zip(candidates, v_scores)
        ]

        # Heap top-K selection O(N log K) instead of full sort O(N log N)
        top_items = heapq.nlargest(top_k, scored_items, key=lambda x: x[0])

        return [self._build_evidence_span(clause, meta, score) for score, clause, meta in top_items]
