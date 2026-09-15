"""
Concurrent Load & Latency Performance Test Suite
"""

import time
import concurrent.futures
from backend.services.ingestion import IngestionService
from backend.services.retrieval import HybridRetrievalService


def test_concurrent_query_load_performance():
    retrieval = HybridRetrievalService()

    doc_text = """MASTER SERVICE AGREEMENT
SECTION 1. TERMINATION NOTICE
Notice requirement is ninety (90) days written notice.

SECTION 2. LIABILITY CAP
Vendor liability is limited to $500,000.
"""
    meta, clauses = IngestionService.parse_document(filename="Perf_Test.txt", content_text=doc_text, tenant_id="tenant_perf")
    retrieval.index_document(meta, clauses)

    queries = [
        "termination notice period",
        "vendor liability cap",
        "written notice requirements",
        "master service agreement terms"
    ] * 25  # 100 concurrent queries

    latencies: list[float] = []

    def execute_single_query(q: str) -> float:
        t0 = time.perf_counter()
        spans = retrieval.search(q, tenant_id="tenant_perf", top_k=5)
        t1 = time.perf_counter()
        assert len(spans) > 0
        return (t1 - t0) * 1000.0  # ms

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(execute_single_query, q) for q in queries]
        for f in concurrent.futures.as_completed(futures):
            latencies.append(f.result())
    total_duration = time.perf_counter() - start_time

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    rps = len(queries) / total_duration

    print(f"\nLOAD PERFORMANCE METRICS (100 Queries @ 10 Threads):")
    print(f"Total Duration: {total_duration:.3f}s | Throughput: {rps:.1f} RPS")
    print(f"p50 Latency: {p50:.2f}ms | p95 Latency: {p95:.2f}ms | p99 Latency: {p99:.2f}ms")

    assert p95 < 1000.0  # p95 must remain under 1000ms for CPU multi-threaded neural transformer inference
    assert rps > 15.0    # RPS target > 15 req/sec on CPU
