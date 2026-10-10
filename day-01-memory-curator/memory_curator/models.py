from dataclasses import dataclass, field
from typing import Literal

MemoryType = Literal["fact", "preference", "task"]


@dataclass(frozen=True)
class Turn:
    turn_id: str
    role: str
    content: str


@dataclass
class MemoryItem:
    kind: MemoryType
    key: str
    value: str
    confidence: float
    evidence: str
    source_turn: str
    review: str = "candidate"
    evidence_turns: list[str] = field(default_factory=list)


@dataclass
class CurationReport:
    memories: list[MemoryItem]
    conflicts: list[dict[str, object]]
    ignored_turns: int

