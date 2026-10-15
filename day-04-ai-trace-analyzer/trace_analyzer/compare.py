"""Baseline/candidate report comparison."""

from typing import Any, Dict, List


def compare(baseline: Dict[str, Any], candidate: Dict[str, Any], latency_threshold: float = 0.20) -> Dict[str, Any]:
    warnings: List[str] = []
    old_p95 = baseline["latency_ms"]["p95"]
    new_p95 = candidate["latency_ms"]["p95"]
    if old_p95 and new_p95 > old_p95 * (1 + latency_threshold):
        warnings.append(f"p95 latency increased from {old_p95:g}ms to {new_p95:g}ms")
    old_rate = baseline["failures"] / baseline["requests"] if baseline["requests"] else 0
    new_rate = candidate["failures"] / candidate["requests"] if candidate["requests"] else 0
    if new_rate > old_rate + 0.05:
        warnings.append(f"failure rate increased from {old_rate:.1%} to {new_rate:.1%}")
    if candidate["estimated_cost"] > baseline["estimated_cost"] * 1.20 and baseline["estimated_cost"]:
        warnings.append("estimated cost increased by more than 20%")
    return {"warnings": warnings, "regression": bool(warnings), "baseline_failure_rate": round(old_rate, 4), "candidate_failure_rate": round(new_rate, 4)}
