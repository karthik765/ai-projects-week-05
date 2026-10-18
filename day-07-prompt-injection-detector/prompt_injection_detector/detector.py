import re
from typing import List

from .models import Finding, Report
from .rules import RULES


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _level(score: int) -> str:
    if score >= 75:
        return "critical"
    if score >= 45:
        return "high"
    if score >= 20:
        return "medium"
    return "low"


def detect(text: str) -> Report:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = _normalize(text)
    findings: List[Finding] = []
    score = 0
    for rule in RULES:
        match = rule.pattern.search(text)
        if not match:
            continue
        evidence = _normalize(match.group(0))[:120]
        findings.append(Finding(rule.category, rule.severity, evidence, rule.rationale, rule.weight))
        score += rule.weight
    score = min(score, 100)
    return Report(score, _level(score), len(normalized), tuple(findings))
