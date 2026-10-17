from typing import Iterable, List

from .models import DroppedMessage, Message, Plan
from .tokenizer import estimate_tokens


def _validate(messages: Iterable[Message], budget: int) -> List[Message]:
    if budget <= 0:
        raise ValueError("budget must be a positive integer")
    result = list(messages)
    for message in result:
        if not message.role or not message.content.strip():
            raise ValueError("every message needs a non-empty role and content")
        if message.priority < 0:
            raise ValueError("priority cannot be negative")
    return result


def plan_context(messages: Iterable[Message], budget: int) -> Plan:
    """Select a stable, useful subset while retaining original conversation order."""
    items = _validate(messages, budget)
    sizes = [estimate_tokens(item.content) for item in items]
    required = [i for i, item in enumerate(items) if item.pinned or item.role == "system"]
    optional = [i for i in range(len(items)) if i not in required]
    selected = []
    warnings = []
    used = 0

    for index in required:
        selected.append(index)
        used += sizes[index]
    if used > budget:
        warnings.append("required messages exceed the budget; all required messages were retained")

    ranked = sorted(
        optional,
        key=lambda i: (items[i].priority, i),
        reverse=True,
    )
    for index in ranked:
        if used + sizes[index] <= budget:
            selected.append(index)
            used += sizes[index]

    selected.sort()
    selected_set = set(selected)
    dropped = []
    for index in range(len(items)):
        if index in selected_set:
            continue
        reason = "required context exceeds budget" if index in required else "lower priority than messages that fit"
        dropped.append(DroppedMessage(index, reason, sizes[index]))
    return Plan(selected, dropped, used, budget, warnings)
