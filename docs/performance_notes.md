# LawPedia Runtime Efficiency & Performance Optimization Report

This document details the 6 runtime efficiency optimizations implemented across LawPedia's request pipeline, event-loop execution, semantic vector search, and contract comparison engine.

---

## Benchmark Comparison Summary

| Metric / Workload | Baseline Timing | Post-Optimization Timing | Speedup / Efficiency Gain |
| :--- | :--- | :--- | :--- |
| **50-Clause Document Ingestion & Indexing** | `39,813.48 ms` | `13,286.16 ms` | **3.0x faster** (66.6% latency reduction) |
| **20 Hybrid Vector Search Queries (200 Clauses)** | `248.43 ms` | `158.60 ms` | **1.57x faster** (36.2% latency reduction) |
| **10 Multi-Dimensional Contract Comparisons** | `24.39 ms` | `22.27 ms` | **1.1x faster** (8.7% latency reduction) |
| **Event Loop Concurrency During Document Upload** | Blocked (100% thread lock) | **Non-Blocking** (Offloaded via thread pool) | Unblocked `/health` and concurrent requests |

---

## Detailed Optimizations Implemented

### Fix 1 — Event Loop Concurrency Offloading (`backend/api/routes.py`)
- **Problem**: `upload_document` was declared `async def`, but performed synchronous parsing (`parse_document`), regex extraction (`extract_obligations`/`extract_rights`), embedding inference (`index_document`), and SQLite disk storage (`save_document_persistent`) directly on the single `asyncio` event loop. This froze all concurrent requests across tenants during uploads.
- **Solution**: Offloaded CPU-bound parsing and I/O-bound indexing to worker threads via `await run_in_threadpool(...)`.
- **Impact**: Keeps the event loop completely free to handle concurrent requests (`/health`, `/query`, metrics) during document uploads.

### Fix 2 — Batched Vector Embedding Generation (`backend/services/retrieval.py`)
- **Problem**: `index_document` previously called `_compute_semantic_embedding(c.text)` in a per-clause Python `for` loop, incurring heavy per-call overhead for SentenceTransformer inference.
- **Solution**: Updated `index_document` to batch encode all clause texts in a single call (`model.encode(texts, convert_to_numpy=True, batch_size=32)`), maintaining unit L2 normalization.
- **Impact**: Cut 50-clause document indexing latency from ~39.8s down to ~13.3s (**3.0x faster**).

### Fix 3 — Tokenized Clause Text Caching (`backend/services/retrieval.py`)
- **Problem**: Lexical BM25 scoring (`_bm25_score`) called `re.findall(r"\w+", text.lower())` fresh on every candidate clause for every single search query.
- **Solution**: Added `self._tokenized_cache: dict[str, list[str]]` populated once at document indexing time, passing pre-tokenized word lists directly to `_bm25_score`.
- **Impact**: Saved thousands of redundant regex string splits per search query.

### Fix 4 — Vectorized Cosine Similarity Matrix Multiplication (`backend/services/retrieval.py`)
- **Problem**: `search()` converted individual candidate clause vectors to numpy arrays and computed pairwise `_cosine_similarity` with repeated vector norm calculations.
- **Solution**: Vectorized candidate vectors into a 2D numpy array (`vectors = np.array(...)`) and computed all cosine similarities in a single dot-product matrix multiplication (`vectors @ query_arr`).
- **Impact**: Eliminated per-clause numpy call overhead and reduced hybrid search query latency across 200 clauses by 36.2%.

### Fix 5 — Heap-Based Top-K Selection (`backend/services/retrieval.py`)
- **Problem**: `search()` used `scored_items.sort(...)` to sort the entire candidate clause list ($O(N \log N)$ complexity).
- **Solution**: Replaced full sorting with `heapq.nlargest(top_k, scored_items, key=lambda x: x[0])` for $O(N \log K)$ selection complexity.
- **Impact**: Optimized algorithm complexity for large multi-document corpora.

### Fix 6 — Precompiled Contract Comparison Regexes (`backend/services/comparison.py`)
- **Problem**: `ComparisonService.DIMENSIONS` stored raw pattern strings that were repeatedly matched with `re.search(...)` during contract comparisons.
- **Solution**: Precompiled all dimension regexes into `re.Pattern` objects (`re.compile(p, re.IGNORECASE)`) at module initialization.
- **Impact**: Removed regex cache lookup overhead during document comparisons.

---

## Verification & Test Results
- **Automated Unit Tests**: All 29 pytest unit tests passed 100% (`29 passed in 17.60s`).
- **Input-Output Equality**: Confirmed identical search rankings, confidence scores, citations, and comparison outputs.
