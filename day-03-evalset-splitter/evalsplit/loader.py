import json
from pathlib import Path
from typing import List


def load_jsonl(path: str | Path) -> List[dict]:
    records: List[dict] = []
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON ({exc.msg})") from exc
        if not isinstance(value, dict) or not isinstance(value.get("text"), str) or not value["text"].strip():
            raise ValueError(f"line {line_number}: each record needs non-empty string field 'text'")
        records.append(value)
    if not records:
        raise ValueError("dataset contains no records")
    return records


def write_jsonl(path: str | Path, records: list[dict]) -> None:
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
