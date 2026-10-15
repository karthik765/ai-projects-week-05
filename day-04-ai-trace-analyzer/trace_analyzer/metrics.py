"""Aggregate trace metrics."""

from collections import Counter
from typing import Any, Dict, Iterable, List

from .parser import TraceRecord


def percentile(values: List[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percent / 100
    lower, upper = int(index), min(int(index) + 1, len(ordered) - 1)
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower), 2)


def analyze(records: Iterable[TraceRecord], input_price: float = 0.000001, output_price: float = 0.000002) -> Dict[str, Any]:
    rows = list(records)
    latencies = [row.latency_ms for row in rows]
    status_counts = Counter(row.status for row in rows)
    model_counts = Counter(row.model for row in rows)
    prompt = sum(row.prompt_tokens for row in rows)
    completion = sum(row.completion_tokens for row in rows)
    slow = sorted(rows, key=lambda row: row.latency_ms, reverse=True)[:3]
    return {
        "requests": len(rows),
        "successful": status_counts.get("ok", 0),
        "failures": len(rows) - status_counts.get("ok", 0),
        "status_counts": dict(status_counts),
        "models": dict(model_counts),
        "latency_ms": {"p50": percentile(latencies, 50), "p95": percentile(latencies, 95), "max": max(latencies, default=0)},
        "tokens": {"prompt": prompt, "completion": completion, "total": prompt + completion},
        "estimated_cost": round(prompt * input_price + completion * output_price, 8),
        "slowest": [{"request_id": row.request_id, "model": row.model, "latency_ms": row.latency_ms} for row in slow],
    }
