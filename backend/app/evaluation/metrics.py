from typing import List, Dict, Any
import math


def calculate_recall_at_k(retrieved: List[str], ground_truth: List[str], k: int) -> float:
    """
    Computes Recall@K: proportion of relevant items retrieved in top-k results.
    """
    if not ground_truth:
        return 1.0
    top_k = retrieved[:k]
    matched = sum(1 for item in ground_truth if any(gt.lower() in r.lower() for r in top_k for gt in [item]))
    return min(1.0, matched / len(ground_truth))


def calculate_precision_at_k(retrieved: List[str], ground_truth: List[str], k: int) -> float:
    """
    Computes Precision@K: proportion of top-k retrieved items that are relevant.
    """
    if k == 0 or not retrieved:
        return 0.0
    top_k = retrieved[:k]
    matched = sum(1 for r in top_k if any(gt.lower() in r.lower() for gt in ground_truth))
    return matched / len(top_k)


def calculate_mrr(retrieved: List[str], ground_truth: List[str]) -> float:
    """
    Computes Mean Reciprocal Rank (MRR) for the first relevant document retrieved.
    """
    for rank, doc in enumerate(retrieved, start=1):
        if any(gt.lower() in doc.lower() for gt in ground_truth):
            return 1.0 / rank
    return 0.0


def calculate_keyword_coverage(text: str, expected_keywords: List[str]) -> float:
    """
    Computes the fraction of expected keywords found in the generated text.
    """
    if not expected_keywords:
        return 1.0
    text_lower = text.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
    return found / len(expected_keywords)


def verify_numerical_exactness(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    rel_tol: float = 0.02
) -> Dict[str, Any]:
    """
    Validates deterministic calculations against expected mathematical values.
    Returns: {"is_exact": bool, "details": dict}
    """
    details = {}
    all_exact = True

    for key, exp_val in expected.items():
        act_val = actual.get(key)
        if act_val is None:
            details[key] = {"status": "missing", "expected": exp_val}
            all_exact = False
            continue

        if isinstance(exp_val, (int, float)):
            try:
                is_close = math.isclose(float(act_val), float(exp_val), rel_tol=rel_tol)
                details[key] = {
                    "status": "pass" if is_close else "fail",
                    "actual": act_val,
                    "expected": exp_val,
                }
                if not is_close:
                    all_exact = False
            except (ValueError, TypeError):
                details[key] = {"status": "type_error", "actual": act_val, "expected": exp_val}
                all_exact = False
        else:
            is_match = str(act_val).strip() == str(exp_val).strip()
            details[key] = {
                "status": "pass" if is_match else "fail",
                "actual": act_val,
                "expected": exp_val,
            }
            if not is_match:
                all_exact = False

    return {"is_exact": all_exact, "details": details}


def verify_mermaid_syntax(mermaid_code: str) -> bool:
    """
    Validates that a Mermaid diagram contains valid header syntax and node connections.
    """
    if not mermaid_code or not isinstance(mermaid_code, str):
        return False
    trimmed = mermaid_code.strip()
    valid_headers = ("graph", "flowchart", "erDiagram", "sequenceDiagram", "classDiagram", "stateDiagram")
    return any(trimmed.startswith(h) for h in valid_headers)
