import time
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.schemas.eglr import DocumentMetadata, ClauseObject
from backend.services.ingestion import IngestionService
from backend.services.extraction import LegalExtractionService
from backend.services.retrieval import HybridRetrievalService
from backend.services.comparison import ComparisonService

def generate_sample_clauses(count: int) -> list[str]:
    templates = [
        "The Provider shall maintain confidentiality of all proprietary materials for a period of 5 years following termination.",
        "Either party may terminate this Agreement upon 30 days prior written notice if the other party breaches any material term.",
        "The total aggregate liability of each party under this Agreement shall be limited to $1,000,000 or total fees paid.",
        "Payments shall be due within 30 days of invoice receipt, incurring 1.5% monthly interest on overdue balances.",
        "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.",
        "The Contractor agrees to indemnify and hold harmless the Client against third-party intellectual property infringement claims.",
        "All patent rights, copyrights, and trade secrets created during performance shall remain sole property of Client.",
        "Any dispute arising out of this Contract shall be resolved through binding arbitration administered by the AAA.",
        "This Agreement automatically renews for successive 1-year terms unless notice of non-renewal is given 60 days prior.",
        "Neither party may assign or transfer its rights or obligations without prior written consent of the other party."
    ]
    clauses = []
    for i in range(count):
        template = templates[i % len(templates)]
        clauses.append(f"Section {i+1}. {template} [Ref Clause {i+1}]")
    return clauses

def benchmark_indexing(clause_count: int = 50):
    text_content = "\n\n".join(generate_sample_clauses(clause_count))
    retrieval = HybridRetrievalService()
    
    start_time = time.perf_counter()
    metadata, clauses = IngestionService.parse_document(
        filename="BenchmarkDoc.txt",
        content_text=text_content,
        mime_type="text/plain",
        tenant_id="tenant_bench"
    )
    for clause in clauses:
        clause.obligations = LegalExtractionService.extract_obligations(clause)
        clause.rights = LegalExtractionService.extract_rights(clause)
    retrieval.index_document(metadata, clauses)
    elapsed = time.perf_counter() - start_time
    return elapsed, retrieval, metadata, clauses

def benchmark_queries(retrieval: HybridRetrievalService, query_count: int = 20):
    queries = [
        "confidentiality period termination",
        "limitation of liability cap amount",
        "written notice termination 30 days",
        "payment due date monthly interest",
        "governing law State of Delaware",
        "indemnify and hold harmless",
        "intellectual property patent rights",
        "binding arbitration dispute AAA",
        "automatic renewal notice 60 days",
        "assignment transfer written consent"
    ]
    
    start_time = time.perf_counter()
    for i in range(query_count):
        q = queries[i % len(queries)]
        results = retrieval.search(query=q, tenant_id="tenant_bench", top_k=5)
    elapsed = time.perf_counter() - start_time
    return elapsed

def benchmark_comparison():
    text_a = "\n\n".join(generate_sample_clauses(30))
    text_b = "\n\n".join(generate_sample_clauses(30))
    meta_a, clauses_a = IngestionService.parse_document("DocA.txt", text_a, "text/plain", "tenant_bench")
    meta_b, clauses_b = IngestionService.parse_document("DocB.txt", text_b, "text/plain", "tenant_bench")
    
    start_time = time.perf_counter()
    for _ in range(10):
        ComparisonService.compare_documents(meta_a, clauses_a, meta_b, clauses_b)
    elapsed = time.perf_counter() - start_time
    return elapsed

if __name__ == "__main__":
    print("Running performance benchmark...")
    
    # 1. 50-clause indexing time
    t_idx_50, ret_service, meta, clauses = benchmark_indexing(50)
    print(f"50-clause indexing: {t_idx_50*1000:.2f} ms")
    
    # 2. 200-clause indexing & 20 queries
    _, ret_200, _, _ = benchmark_indexing(200)
    t_queries_20 = benchmark_queries(ret_200, 20)
    print(f"20 queries over 200 clauses: {t_queries_20*1000:.2f} ms")
    
    # 3. 10 contract comparisons
    t_comp_10 = benchmark_comparison()
    print(f"10 document comparisons: {t_comp_10*1000:.2f} ms")
