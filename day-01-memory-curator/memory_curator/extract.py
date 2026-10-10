import re

from .models import MemoryItem, Turn

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")
TOKEN = re.compile(r"\b(?:sk|ghp|xoxb|bearer)[-_A-Za-z0-9.]{8,}\b", re.I)

PREFERENCE_PATTERNS = [
    (re.compile(r"\bI prefer (?P<value>.+)", re.I), "preference", 0.92),
    (re.compile(r"\bI like (?P<value>.+)", re.I), "preference", 0.86),
    (re.compile(r"\bI usually use (?P<value>.+)", re.I), "preference", 0.84),
]
FACT_PATTERNS = [
    (re.compile(r"\bremember(?: that)? (?P<value>.+)", re.I), "fact", 0.95),
    (re.compile(r"\bmy (?P<key>[\w -]+?) is (?P<value>.+)", re.I), "fact", 0.9),
    (re.compile(r"\bI am (?P<value>.+)", re.I), "fact", 0.78),
]
TASK_PATTERN = re.compile(r"\b(?:I need to|please remind me to|TODO:?) (?P<value>.+)", re.I)


def _safe(text: str) -> str:
    text = EMAIL.sub("[email]", text)
    text = PHONE.sub("[phone]", text)
    return TOKEN.sub("[token]", text).strip().rstrip(".!?")


def _key(kind: str, raw_key: str, value: str) -> str:
    if raw_key:
        return re.sub(r"\s+", "_", raw_key.lower().strip())
    words = re.findall(r"[a-z0-9]+", value.lower())[:4]
    return f"{kind}:" + "_".join(words)


def extract_turn(turn: Turn) -> list[MemoryItem]:
    if turn.role.lower() not in {"user", "human"}:
        return []
    found: list[MemoryItem] = []
    for pattern, kind, confidence in PREFERENCE_PATTERNS + FACT_PATTERNS:
        match = pattern.search(turn.content)
        if match:
            value = _safe(match.group("value"))
            raw_key = match.groupdict().get("key", "")
            if value:
                found.append(MemoryItem(kind, _key(kind, raw_key, value), value, confidence, _safe(turn.content), turn.turn_id))
                return found
    match = TASK_PATTERN.search(turn.content)
    if match:
        value = _safe(match.group("value"))
        if value:
            found.append(MemoryItem("task", _key("task", "", value), value, 0.88, _safe(turn.content), turn.turn_id))
    return found
