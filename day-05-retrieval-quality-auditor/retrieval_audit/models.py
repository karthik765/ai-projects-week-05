from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalCase:
    query_id: str
    relevant_ids: tuple[str, ...]
    retrieved_ids: tuple[str, ...]
    cited_ids: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any], line_number: int) -> "RetrievalCase":
        query_id = str(data.get("query_id", "")).strip()
        relevant = tuple(str(item) for item in data.get("relevant_ids", []))
        retrieved = tuple(str(item) for item in data.get("retrieved_ids", []))
        cited = tuple(str(item) for item in data.get("cited_ids", []))
        errors = []
        if not query_id:
            errors.append("query_id is required")
        if not relevant:
            errors.append("relevant_ids must not be empty")
        if len(set(retrieved)) != len(retrieved):
            errors.append("retrieved_ids contains duplicates")
        if errors:
            raise ValueError(f"line {line_number}: " + "; ".join(errors))
        return cls(query_id, relevant, retrieved, cited)
