# LawPedia Performance & Runtime Optimization Benchmarks

## Overview
This document records empirical performance benchmarks across LawPedia's backend database persistence, retrieval engine, API routing, and frontend asset delivery.

---

## 1. Database & Cold-Start Optimization (Fixes 1–6)

### 1.1 Persisted Embeddings & Fast-Path Cache Reload (`Fix 1`)
- **Metric**: Cold-start `reload_stores_from_db()` execution time for a corpus of 20 documents comprising 500 clauses.
- **Without Cache (Full Re-embedding)**: Recomputed embeddings for 500 clauses sequentially using PyTorch/SentenceTransformers.
- **With Cache (`index_document_from_cache`)**: **158.32 ms** (reads pre-computed unit vectors and token frequencies directly from SQLite in 2 batch queries).

### 1.2 Database Connection & WAL Mode (`Fix 2 & Fix 6`)
- Replaced per-function `sqlite3.connect()` / `conn.close()` with thread-safe singleton connection manager (`get_connection()`).
- Enabled `PRAGMA journal_mode=WAL` for concurrent read/write locks during background indexing.

### 1.3 Schema Initialization & Migrations (`Fix 3`)
- Moved schema creation, column migrations (`embedding_json`, `tokens_json`), and index initialization to application startup (`main.py` lifespan).
- Eliminated redundant `init_db()` calls on every API operation.

### 1.4 Database Indexing & Query Plan (`Fix 4`)
- Added indexes:
  - `idx_documents_tenant ON documents(tenant_id)`
  - `idx_clauses_document ON clauses(document_id)`
  - `idx_clauses_tenant ON clauses(tenant_id)`
- **`EXPLAIN QUERY PLAN` Verification**:
  ```sql
  EXPLAIN QUERY PLAN SELECT metadata_json FROM documents WHERE tenant_id = 'tenant_lawpedia_demo';
  -- Result: SEARCH documents USING INDEX idx_documents_tenant (tenant_id=?)
  ```

### 1.5 Elimination of $N+1$ Queries & Batch Clause Insertion (`Fix 5`)
- Refactored `load_all_persistent_data()` to query metadata, clauses, embeddings, and tokens in **2 queries total** instead of $1 + N$ queries.
- Refactored `save_document_persistent()` to use `cursor.executemany()` for single-transaction clause persistence.

---

## 2. In-Memory Search & Regex Precompilation Engine

### 2.1 Retrieval Engine Vectorization & Token Frequency Caching
- **Pytest Suite (`pytest tests/ -q`)**:
  - Baseline: **49.81s**
  - Optimized: **18.43s** (⚡ **63.0% total runtime reduction**)
- **20 Queries over 200 Clauses**:
  - Baseline: **176.35 ms**
  - Optimized: **121.79 ms** (⚡ **30.9% latency reduction**)

### 2.2 Regex Pattern Precompilation
- Precompiled regex patterns across `LegalExtractionService`, `IngestionService`, `LegalSimplificationService`, and `FalsePremiseDetector` at module scope to eliminate per-string regex string parsing overhead.

---

## 3. Frontend Bundle Code-Splitting (`Fix 7`)

- **Vite Build Output (`npm run build`)**:
  - **Monolithic Initial Bundle (Before)**: `dist/assets/index-C93UChBw.js` — **349.66 kB** (gzip: 88.62 kB)
  - **Code-Split Initial Bundle (After)**: `dist/assets/index-Bavkyw6W.js` — **314.55 kB** (gzip: 83.21 kB)
  - **Initial JS Size Reduction**: ⚡ **35.11 kB initial payload reduction**

- **Dynamically Loaded Secondary View Chunks**:
  - `ContractComparison-BRz7u_rJ.js`: 4.96 kB
  - `LawyerHandoffView-Ctaxvr-B.js`: 6.92 kB
  - `SecurityMetricsDashboard-B1Da-ixa.js`: 7.70 kB
  - `DocumentWorkspaceView-CzJR6eB9.js`: 17.76 kB
