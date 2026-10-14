import argparse
import json
import sys
from pathlib import Path

from .loader import load_jsonl, write_jsonl
from .models import SplitConfig
from .splitter import split_records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create deterministic, leakage-aware JSONL dataset splits.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("out"))
    parser.add_argument("--seed", default="default")
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--validation", type=float, default=0.1)
    parser.add_argument("--test", type=float, default=0.1)
    args = parser.parse_args(argv)
    try:
        result = split_records(load_jsonl(args.input), SplitConfig(args.train, args.validation, args.test, args.seed))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, records in result.splits.items():
        write_jsonl(args.output / f"{name}.jsonl", records)
    report = dict(result.report)
    report["warnings"] = result.warnings
    (args.output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if result.warnings else 0


if __name__ == "__main__":
    sys.exit(main())
