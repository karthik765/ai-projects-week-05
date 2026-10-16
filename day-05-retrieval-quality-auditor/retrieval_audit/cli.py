import argparse
import json
from pathlib import Path

from .loader import load_jsonl
from .metrics import audit_records, compare_audits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit retrieval quality from JSONL records.")
    parser.add_argument("input", help="JSONL file with query, relevant, and retrieved IDs")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print machine-readable output")
    parser.add_argument("--compare", metavar="BASELINE", help="compare this run with a baseline JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = audit_records(load_jsonl(args.input))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    if args.compare:
        baseline = json.loads(Path(args.compare).read_text(encoding="utf-8"))
        report["warnings"] = compare_audits(baseline, report)
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Cases: {report['cases']}")
        print(f"MRR: {report['mrr']:.4f} | Mean recall: {report['mean_recall']:.4f}")
        for k, values in report["k"].items():
            print(f"Hit@{k}: {values['hit_rate']:.4f}")
        if report.get("citation_coverage") is not None:
            print(f"Citation coverage: {report['citation_coverage']:.4f}")
        for warning in report.get("warnings", []):
            print(f"WARNING: {warning}")
    return 0
