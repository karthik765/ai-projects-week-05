# AI Trace Analyzer

Analyze JSONL traces from AI applications without sending telemetry anywhere.
The analyzer summarizes request count, errors, latency percentiles, token usage,
estimated cost, model mix, and slow or failed requests. It also compares two
reports to flag regressions.

## Quick start

From this directory, run:

```text
python -m trace_analyzer.cli examples/traces.jsonl
python -m trace_analyzer.cli examples/traces.jsonl --json
python -m trace_analyzer.cli examples/baseline.jsonl --compare examples/candidate.jsonl
python -m unittest discover -s tests -v
```

The project uses only the Python standard library. Trace records are JSON
objects with `request_id`, `model`, `latency_ms`, `prompt_tokens`,
`completion_tokens`, and optional `status`/`error` fields. Missing optional
fields receive safe defaults; malformed records are reported rather than
crashing the entire run.

## Example record

```json
{"request_id":"r-1","model":"atlas-mini","latency_ms":410,"prompt_tokens":120,"completion_tokens":48,"status":"ok"}
```

Cost estimates use the explicitly supplied pricing profile in
`trace_analyzer/pricing.py`; the sample prices are illustrative and are not
live billing rates. Use `--input-price` and `--output-price` when you want a
different estimate.

## Design

- `parser.py` validates and normalizes JSONL records while preserving issue details.
- `metrics.py` computes transparent aggregates and percentile values.
- `compare.py` turns baseline/candidate reports into actionable regression warnings.
- `cli.py` provides human-readable and JSON output suitable for local checks or CI.

No API key or network connection is required.
