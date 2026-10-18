from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Finding:
    category: str
    severity: str
    evidence: str
    rationale: str
    weight: int


@dataclass(frozen=True)
class Report:
    score: int
    risk_level: str
    normalized_length: int
    findings: Tuple[Finding, ...]

    @property
    def is_suspicious(self) -> bool:
        return bool(self.findings)
