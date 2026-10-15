"""JSONL parsing and record normalization."""

import json
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional


@dataclass
class TraceRecord:
    request_id: str
    model: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    status: str = "ok"
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def _number(value: Any, field: str, integer: bool = False) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    if value < 0:
        raise ValueError(f"{field} must be non-negative")
    return int(value) if integer else float(value)


def normalize(payload: dict, line_number: int) -> TraceRecord:
    if not isinstance(payload, dict):
        raise ValueError(f"line {line_number}: expected a JSON object")
    request_id = str(payload.get("request_id", "")).strip()
    model = str(payload.get("model", "unknown")).strip() or "unknown"
    if not request_id:
        raise ValueError(f"line {line_number}: request_id is required")
    status = str(payload.get("status", "ok")).lower()
    if status not in {"ok", "error", "timeout"}:
        raise ValueError(f"line {line_number}: unsupported status {status!r}")
    return TraceRecord(
        request_id=request_id,
        model=model,
        latency_ms=_number(payload.get("latency_ms", 0), "latency_ms"),
        prompt_tokens=_number(payload.get("prompt_tokens", 0), "prompt_tokens", True),
        completion_tokens=_number(payload.get("completion_tokens", 0), "completion_tokens", True),
        status=status,
        error=str(payload["error"]) if payload.get("error") else None,
    )


def read_jsonl(lines: Iterable[str]) -> tuple[List[TraceRecord], List[str]]:
    records: List[TraceRecord] = []
    issues: List[str] = []
    for line_number, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            records.append(normalize(json.loads(raw), line_number))
        except (json.JSONDecodeError, ValueError) as exc:
            issues.append(str(exc))
    return records, issues
