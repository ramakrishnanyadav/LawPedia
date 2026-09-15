"""
Golden Evaluation Benchmark Pytest Runner
"""

import json
from backend.services.evaluation import run_golden_evaluation


def test_golden_dataset_execution():
    results = run_golden_evaluation()
    print("GOLDEN BENCHMARK RESULTS:\n", json.dumps(results, indent=2))
    assert results["total_test_queries"] == 25
    assert results["retrieval_precision"] >= 0.70
    assert results["retrieval_recall"] >= 0.70
    assert results["contradiction_detection_rate_cdr"] >= 0.70


if __name__ == "__main__":
    r = run_golden_evaluation()
    print(json.dumps(r, indent=2))

