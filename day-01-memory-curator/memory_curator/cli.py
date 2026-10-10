import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .curator import curate
from .models import Turn


def load_turns(path: Path) -> list[Turn]:
    turns = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        data = json.loads(line)
        turns.append(Turn(str(data.get("id", number)), data["role"], data["content"]))
    return turns


def markdown(report) -> str:
    lines = ["# Memory candidates", "", f"Ignored turns: {report.ignored_turns}", ""]
    for item in report.memories:
        lines += [f"- **{item.kind} — {item.key}**: {item.value} (confidence {item.confidence:.2f}; review: {item.review})", f"  Evidence ({item.source_turn}): {item.evidence}"]
    if report.conflicts:
        lines += ["", "## Conflicts"]
        for conflict in report.conflicts:
            lines.append(f"- `{conflict['key']}`: " + " vs ".join(map(str, conflict["values"])))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract reviewable memory candidates from JSONL chat turns")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--min-confidence", type=float, default=0.0)
    args = parser.parse_args()
    report = curate(load_turns(args.input))
    report.memories = [item for item in report.memories if item.confidence >= args.min_confidence]
    if args.format == "markdown":
        print(markdown(report), end="")
    else:
        print(json.dumps(asdict(report), indent=2))


if __name__ == "__main__":
    main()
