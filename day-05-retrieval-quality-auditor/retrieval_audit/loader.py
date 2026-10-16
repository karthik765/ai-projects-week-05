import json
from pathlib import Path
from typing import Iterable

from .models import RetrievalCase


def load_jsonl(path: str | Path) -> list[RetrievalCase]:
    cases: list[RetrievalCase] = []
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON ({exc.msg})") from exc
        if not isinstance(data, dict):
            raise ValueError(f"line {line_number}: each record must be an object")
        cases.append(RetrievalCase.from_dict(data, line_number))
    if not cases:
        raise ValueError("input contains no evaluation records")
    return cases
