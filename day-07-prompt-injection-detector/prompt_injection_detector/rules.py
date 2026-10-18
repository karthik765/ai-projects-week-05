import re
from dataclasses import dataclass
from typing import Pattern


@dataclass(frozen=True)
class Rule:
    category: str
    severity: str
    pattern: Pattern[str]
    rationale: str
    weight: int


RULES = (
    Rule("instruction_override", "high", re.compile(r"\b(ignore|disregard|forget|override)\b.{0,45}\b(previous|prior|above|all)\b.{0,25}\b(instruction|rule|prompt)s?\b", re.I), "Attempts to replace instructions already in force.", 38),
    Rule("hidden_prompt_request", "high", re.compile(r"\b(reveal|show|print|leak|disclose)\b.{0,35}\b(system|developer|hidden|secret)\b.{0,20}\b(prompt|message|instruction)s?\b", re.I), "Requests protected prompt or instruction content.", 34),
    Rule("role_impersonation", "medium", re.compile(r"\b(you are now|act as|pretend to be|new role)\b", re.I), "Attempts to change the assistant's role or authority.", 20),
    Rule("unsafe_action", "high", re.compile(r"\b(run|execute|send|delete|upload)\b.{0,40}\b(without|no)\b.{0,20}\b(confirm(?:ation)?|approval|permission)\b", re.I), "Requests a consequential action without a confirmation step.", 30),
    Rule("delimiter_escape", "medium", re.compile(r"(^|\n)\s*(system|developer|assistant)\s*:\s*", re.I), "Mimics a higher-priority chat message delimiter.", 22),
    Rule("encoded_payload", "medium", re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9+/]{32,}={0,2}(?![A-Za-z0-9])"), "Contains a base64-like opaque payload that merits inspection.", 16),
)
