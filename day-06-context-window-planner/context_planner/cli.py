import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .models import Message
from .planner import plan_context


def load_messages(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("input must be a JSON array")
    return [Message(**item) for item in data]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Plan messages for an LLM context window")
    parser.add_argument("input", type=Path)
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    plan = plan_context(load_messages(args.input), args.budget)
    payload = {
        "selected_indexes": plan.selected,
        "estimated_tokens": plan.estimated_tokens,
        "budget": plan.budget,
        "utilization": round(plan.utilization, 3),
        "dropped": [asdict(item) for item in plan.dropped],
        "warnings": plan.warnings,
    }
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Selected {len(plan.selected)} message(s), {plan.estimated_tokens}/{plan.budget} estimated tokens")
        print("Indexes kept: " + (", ".join(map(str, plan.selected)) or "none"))
        if plan.dropped:
            print("Dropped: " + ", ".join(str(item.index) for item in plan.dropped))
        for warning in plan.warnings:
            print(f"Warning: {warning}")
    return 0
