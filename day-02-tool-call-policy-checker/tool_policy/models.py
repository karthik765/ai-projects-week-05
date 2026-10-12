"""Data models used by the policy checker."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    call_id: Optional[str] = None

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "ToolCall":
        if not isinstance(value, dict) or not isinstance(value.get("name"), str):
            raise ValueError("each tool call needs a string 'name'")
        args = value.get("arguments", {})
        if not isinstance(args, dict):
            raise ValueError("tool call arguments must be an object")
        return cls(value["name"], args, value.get("id") or value.get("call_id"))


@dataclass(frozen=True)
class Policy:
    allowed_tools: List[str]
    blocked_tools: List[str] = field(default_factory=list)
    blocked_argument_keys: List[str] = field(default_factory=list)
    require_confirmation_for: List[str] = field(default_factory=list)
    max_calls: int = 10
    deny_unknown_tools: bool = True

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Policy":
        if not isinstance(value, dict):
            raise ValueError("policy must be an object")
        allowed = value.get("allowed_tools", [])
        if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
            raise ValueError("allowed_tools must be a list of strings")
        max_calls = value.get("max_calls", 10)
        if not isinstance(max_calls, int) or max_calls < 1:
            raise ValueError("max_calls must be a positive integer")
        fields = {}
        for key in ("blocked_tools", "blocked_argument_keys", "require_confirmation_for"):
            items = value.get(key, [])
            if not isinstance(items, list) or not all(isinstance(x, str) for x in items):
                raise ValueError(f"{key} must be a list of strings")
            fields[key] = items
        return cls(allowed, max_calls=max_calls, deny_unknown_tools=value.get("deny_unknown_tools", True), **fields)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    call_index: Optional[int] = None
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "severity": self.severity, "message": self.message}
        if self.call_index is not None:
            result["call_index"] = self.call_index
        if self.evidence is not None:
            result["evidence"] = self.evidence
        return result
