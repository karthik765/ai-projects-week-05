import re
from collections import defaultdict

from .models import MemoryItem


def canonical(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", value.lower()).strip()


def merge_duplicates(items: list[MemoryItem]) -> list[MemoryItem]:
    merged: dict[tuple[str, str], MemoryItem] = {}
    for item in items:
        key = (item.kind, item.key)
        existing = merged.get(key)
        if existing is None:
            item.evidence_turns = [item.source_turn]
            merged[key] = item
        elif canonical(existing.value) == canonical(item.value):
            existing.confidence = max(existing.confidence, item.confidence)
            existing.evidence_turns.append(item.source_turn)
            existing.evidence += f" | {item.evidence}"
        else:
            item.review = "conflict"
            item.evidence_turns = [item.source_turn]
            merged[(item.kind, f"{item.key}:{len(merged)}")] = item
    return list(merged.values())


def find_conflicts(items: list[MemoryItem]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[MemoryItem]] = defaultdict(list)
    for item in items:
        grouped[(item.kind, item.key.split(":")[0])].append(item)
    conflicts = []
    for (kind, key), values in grouped.items():
        distinct = {canonical(item.value) for item in values}
        if len(distinct) > 1:
            conflicts.append({"kind": kind, "key": key, "values": [item.value for item in values], "review": "choose-current-value"})
    return conflicts
