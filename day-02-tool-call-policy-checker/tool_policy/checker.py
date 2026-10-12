"""Deterministic, explainable checks for model-generated tool calls."""

from dataclasses import asdict
from typing import Any, Dict, Iterable, List

from .models import Finding, Policy, ToolCall


class PolicyChecker:
    def __init__(self, policy: Policy):
        self.policy = policy

    def check(self, calls: Iterable[ToolCall]) -> Dict[str, Any]:
        calls = list(calls)
        findings: List[Finding] = []
        if len(calls) > self.policy.max_calls:
            findings.append(Finding("CALL_LIMIT", "high", f"{len(calls)} calls exceed the limit of {self.policy.max_calls}"))
        for index, call in enumerate(calls):
            findings.extend(self._check_call(call, index))
        severities = {finding.severity for finding in findings}
        status = "deny" if "high" in severities or "critical" in severities else ("review" if findings else "allow")
        return {
            "status": status,
            "call_count": len(calls),
            "risk_score": self._risk_score(findings),
            "findings": [finding.to_dict() for finding in findings],
        }

    def _check_call(self, call: ToolCall, index: int) -> List[Finding]:
        result: List[Finding] = []
        if call.name in self.policy.blocked_tools:
            result.append(Finding("BLOCKED_TOOL", "critical", f"Tool '{call.name}' is explicitly blocked", index, call.name))
        elif self.policy.deny_unknown_tools and call.name not in self.policy.allowed_tools:
            result.append(Finding("UNKNOWN_TOOL", "high", f"Tool '{call.name}' is not in the allowlist", index, call.name))
        if call.name in self.policy.require_confirmation_for:
            result.append(Finding("CONFIRMATION_REQUIRED", "medium", f"Tool '{call.name}' requires human confirmation", index, call.name))
        for key in sorted(set(call.arguments) & set(self.policy.blocked_argument_keys)):
            result.append(Finding("BLOCKED_ARGUMENT", "high", f"Argument '{key}' is not permitted for '{call.name}'", index, key))
        return result

    @staticmethod
    def _risk_score(findings: List[Finding]) -> int:
        weights = {"critical": 100, "high": 70, "medium": 30, "low": 10}
        return min(100, sum(weights.get(item.severity, 0) for item in findings))
