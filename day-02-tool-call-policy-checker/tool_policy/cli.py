"""Command-line interface for checking a JSON tool-call batch."""

import argparse
import json
import sys
from pathlib import Path

from .checker import PolicyChecker
from .models import Policy, ToolCall


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check model tool calls against a local policy")
    parser.add_argument("input", type=Path, help="JSON file containing policy and calls")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print machine-readable output")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        policy = Policy.from_dict(payload["policy"])
        calls = [ToolCall.from_dict(item) for item in payload.get("calls", [])]
        report = PolicyChecker(policy).check(calls)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Status: {report['status'].upper()} | risk {report['risk_score']}/100 | calls {report['call_count']}")
        for finding in report["findings"]:
            location = "" if "call_index" not in finding else f" call {finding['call_index'] + 1}:"
            print(f"- {finding['severity'].upper()} {finding['code']}{location} {finding['message']}")
    return 0 if report["status"] == "allow" else 1


if __name__ == "__main__":
    raise SystemExit(main())
