from collections import Counter
from typing import Any, Iterable

from .models import RetrievalCase


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def audit_records(cases: list[RetrievalCase], k_values: tuple[int, ...] = (1, 3, 5)) -> dict[str, Any]:
    if not cases:
        raise ValueError("at least one case is required")
    metrics: dict[str, Any] = {"cases": len(cases), "k": {}}
    for k in k_values:
        hits = [bool(set(case.retrieved_ids[:k]) & set(case.relevant_ids)) for case in cases]
        metrics["k"][str(k)] = {"hit_rate": round(_mean(float(v) for v in hits), 4)}

    reciprocal_ranks = []
    recalls = []
    citation_coverage = []
    missed: list[str] = []
    for case in cases:
        rank = next((index + 1 for index, item in enumerate(case.retrieved_ids) if item in case.relevant_ids), None)
        reciprocal_ranks.append(1 / rank if rank else 0.0)
        recalls.append(len(set(case.relevant_ids) & set(case.retrieved_ids)) / len(set(case.relevant_ids)))
        if case.cited_ids:
            citation_coverage.append(len(set(case.cited_ids) & set(case.relevant_ids)) / len(set(case.relevant_ids)))
        if not set(case.retrieved_ids[: max(k_values)]) & set(case.relevant_ids):
            missed.append(case.query_id)
    metrics.update({
        "mrr": round(_mean(reciprocal_ranks), 4),
        "mean_recall": round(_mean(recalls), 4),
        "citation_coverage": round(_mean(citation_coverage), 4) if citation_coverage else None,
        "missed_query_ids": missed,
    })
    return metrics


def compare_audits(baseline: dict[str, Any], candidate: dict[str, Any], tolerance: float = 0.02) -> list[str]:
    warnings = []
    for name in ("mrr", "mean_recall"):
        if candidate.get(name, 0) + tolerance < baseline.get(name, 0):
            warnings.append(f"{name} regressed from {baseline[name]:.4f} to {candidate[name]:.4f}")
    return warnings
