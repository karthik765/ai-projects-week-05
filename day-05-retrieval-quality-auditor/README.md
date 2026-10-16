# Retrieval Quality Auditor

Retrieval pipelines can look healthy while silently missing the documents needed to answer a question. This dependency-free utility audits JSONL retrieval results with explainable ranking metrics and can compare a candidate run with a baseline.

## Features

- Hit rate at configurable built-in cutoffs (1, 3, and 5)
- Mean reciprocal rank (MRR) and mean recall
- Optional relevant-document citation coverage
- Missed query IDs for quick investigation
- Input validation and regression warnings
- Human-readable or JSON CLI output

Each input line is an object with `query_id`, `relevant_ids`, `retrieved_ids`, and optional `cited_ids`. IDs are opaque strings, so the tool works with vector, keyword, or hybrid retrieval exports.

## Run

From this directory:

```text
python -m retrieval_audit examples/retrievals.jsonl
python -m retrieval_audit examples/retrievals.jsonl --json
python -m unittest discover -s tests -v
```

To compare a run with a previously saved JSON report:

```text
python -m retrieval_audit examples/retrievals.jsonl --compare baseline-report.json
```

The tool does not call an LLM, fetch documents, or claim that lexical metrics replace human answer-quality review. Use the missed IDs and regression warnings to select cases for deeper evaluation.
