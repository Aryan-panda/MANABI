import pytest
from app.evaluation.metrics import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr,
    calculate_keyword_coverage,
    verify_numerical_exactness,
    verify_mermaid_syntax,
)
from app.evaluation.runner import BenchmarkEvaluationRunner


def test_retrieval_ranking_metrics():
    retrieved = ["Course Handbook", "Attendance Rules", "Disciplinary Code"]
    ground_truth = ["Attendance Rules"]

    # Attendance Rules is at rank 2
    assert calculate_recall_at_k(retrieved, ground_truth, k=2) == 1.0
    assert calculate_recall_at_k(retrieved, ground_truth, k=1) == 0.0
    assert calculate_precision_at_k(retrieved, ground_truth, k=2) == 0.5
    assert calculate_mrr(retrieved, ground_truth) == 0.5


def test_keyword_coverage():
    text = "The attendance threshold is 75% for regular students and 65% with condonation."
    keywords = ["75%", "condonation", "medical"]
    cov = calculate_keyword_coverage(text, keywords)
    assert cov == pytest.approx(2 / 3, rel=1e-2)


def test_verify_numerical_exactness():
    actual = {"average_total_qps": 57.87, "peak_total_qps": 144.68}
    expected = {"average_total_qps": 57.87, "peak_total_qps": 144.68}
    res = verify_numerical_exactness(actual, expected)
    assert res["is_exact"]

    bad_actual = {"average_total_qps": 99.99}
    res_bad = verify_numerical_exactness(bad_actual, expected)
    assert not res_bad["is_exact"]


def test_verify_mermaid_syntax():
    valid_chart = "flowchart TB\n  A --> B"
    assert verify_mermaid_syntax(valid_chart)

    invalid_chart = "Some random text without diagram header"
    assert not verify_mermaid_syntax(invalid_chart)


@pytest.mark.asyncio
async def test_full_benchmark_runner_passes():
    runner = BenchmarkEvaluationRunner()
    report = await runner.run()
    assert report["status"] == "PASS"
    assert report["routing_accuracy_percentage"] >= 80.0
    assert report["deterministic_math_accuracy_percentage"] == 100.0
    assert report["mermaid_syntax_validity_percentage"] == 100.0
