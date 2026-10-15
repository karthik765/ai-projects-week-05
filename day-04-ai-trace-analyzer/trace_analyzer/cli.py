"""Command-line interface for the trace analyzer."""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from .compare import compare
from .metrics import analyze
from .parser import read_jsonl


def load(path: str, args: argparse.Namespace) -> tuple[Dict[str, Any], list[str]]:
    records, issues = read_jsonl(Path(path).read_text(encoding="utf-8").splitlines())
    return analyze(records, args.input_price, args.output_price), issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize local AI application JSONL traces.")
    parser.add_argument("input", help="JSONL trace file")
    parser.add_argument("--compare", dest="candidate", help="candidate JSONL file to compare against input")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--input-price", type=float, default=0.000001)
    parser.add_argument("--output-price", type=float, default=0.000002)
    args = parser.parse_args()
    report, issues = load(args.input, args)
    result: Dict[str, Any] = {"report": report, "issues": issues}
    if args.candidate:
        candidate, candidate_issues = load(args.candidate, args)
        result["candidate"] = candidate
        result["comparison"] = compare(report, candidate)
        result["issues"] += candidate_issues
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Requests: {report['requests']} | failures: {report['failures']} | p95: {report['latency_ms']['p95']}ms")
        print(f"Tokens: {report['tokens']['total']} | estimated cost: ${report['estimated_cost']:.8f}")
        if issues:
            print(f"Skipped records: {len(issues)}")
        if args.candidate:
            for warning in result["comparison"]["warnings"] or ["No regression warnings"]:
                print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
