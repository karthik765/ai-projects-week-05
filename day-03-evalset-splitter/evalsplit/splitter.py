import hashlib
import re
from collections import Counter, defaultdict
from typing import Iterable

from .models import SplitConfig, SplitResult


def _text_key(record: dict, fields: tuple[str, ...]) -> str:
    values = [str(record.get(field, "")).strip().lower() for field in fields]
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def _bucket(record: dict, index: int, seed: str) -> int:
    identity = str(record.get("id", "")) or f"{index}:{record.get('text', '')}"
    digest = hashlib.sha256(f"{seed}\0{identity}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def _choose_split(value: float, config: SplitConfig) -> str:
    train_end = config.train_ratio
    validation_end = train_end + config.validation_ratio
    if value < train_end:
        return "train"
    if value < validation_end:
        return "validation"
    return "test"


def split_records(records: Iterable[dict], config: SplitConfig = SplitConfig()) -> SplitResult:
    items = list(records)
    if not items:
        raise ValueError("dataset contains no records")
    warnings: list[str] = []
    exact_groups: dict[str, list[int]] = defaultdict(list)
    normalized_groups: dict[str, list[int]] = defaultdict(list)
    for i, record in enumerate(items):
        exact_groups[json_identity(record)].append(i)
        normalized_groups[_text_key(record, config.text_fields)].append(i)
    exact_dupes = [group for group in exact_groups.values() if len(group) > 1]
    normalized_dupes = [group for group in normalized_groups.values() if len(group) > 1]
    if exact_dupes:
        warnings.append(f"{sum(len(g) - 1 for g in exact_dupes)} exact duplicate record(s)")
    if normalized_dupes:
        warnings.append(f"{sum(len(g) - 1 for g in normalized_dupes)} normalized text duplicate(s)")

    by_label: dict[str, list[int]] = defaultdict(list)
    for i, record in enumerate(items):
        by_label[str(record.get("label", "__unlabeled__"))].append(i)
    assignments: dict[int, str] = {}
    for indexes in by_label.values():
        ordered = sorted(indexes, key=lambda i: _bucket(items[i], i, config.seed))
        total = len(ordered)
        for rank, index in enumerate(ordered):
            assignments[index] = _choose_split((rank + 0.5) / total, config)
    splits = {name: [] for name in ("train", "validation", "test")}
    for index, record in enumerate(items):
        splits[assignments[index]].append(record)

    leakage = 0
    seen: dict[str, str] = {}
    for split_name, split_records_list in splits.items():
        for record in split_records_list:
            key = _text_key(record, config.text_fields)
            if key in seen and seen[key] != split_name:
                leakage += 1
            seen[key] = split_name
    if leakage:
        warnings.append(f"{leakage} normalized text item(s) cross split boundaries")
    report = {
        "total": len(items),
        "counts": {name: len(values) for name, values in splits.items()},
        "labels": {name: dict(Counter(str(r.get("label", "__unlabeled__")) for r in values)) for name, values in splits.items()},
        "exact_duplicate_groups": len(exact_dupes),
        "normalized_duplicate_groups": len(normalized_dupes),
        "cross_split_leakage_items": leakage,
        "seed": config.seed,
    }
    return SplitResult(splits=splits, report=report, warnings=warnings)


def json_identity(record: dict) -> str:
    import json
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
