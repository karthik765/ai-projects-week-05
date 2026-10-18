import argparse
import json
from pathlib import Path
from typing import Any

from .detector import detect


def _payload(report: Any) -> dict:
    return {"score": report.score, "risk_level": report.risk_level, "suspicious": report.is_suspicious, "normalized_length": report.normalized_length, "findings": [f.__dict__ for f in report.findings]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage text for prompt-injection signals")
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = detect(args.path.read_text(encoding="utf-8"))
    if args.as_json:
        print(json.dumps(_payload(report), indent=2))
    else:
        print(f"Risk: {report.risk_level} ({report.score}/100)")
        if not report.findings:
            print("No configured injection signals found.")
        for finding in report.findings:
            print(f"- [{finding.severity}] {finding.category}: {finding.evidence}")
            print(f"  {finding.rationale}")
    return 0
