from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Message:
    role: str
    content: str
    priority: int = 0
    pinned: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DroppedMessage:
    index: int
    reason: str
    estimated_tokens: int


@dataclass(frozen=True)
class Plan:
    selected: List[int]
    dropped: List[DroppedMessage]
    estimated_tokens: int
    budget: int
    warnings: List[str]

    @property
    def utilization(self) -> float:
        return self.estimated_tokens / self.budget if self.budget else 0.0
