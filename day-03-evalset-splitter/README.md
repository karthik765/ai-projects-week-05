# Evalset Splitter

Evalset Splitter turns a JSONL dataset into deterministic train, validation, and test files for AI evaluation. It uses stable content hashes so reruns produce the same split, keeps label proportions close to the source distribution, and reports duplicate or cross-split leakage risks.

## Features

- deterministic hash-based assignment with configurable ratios and seed;
- stratified allocation for an optional `label` field;
- exact duplicate detection and normalized text leakage checks;
- JSON report with counts, label distributions, and warnings;
- standard-library-only CLI and automated tests.

## Input

Each line is a JSON object. `id` is optional but recommended; `text` is required. An optional `label` is used for stratification.

```json
{"id":"ex-1","text":"The assistant should cite sources.","label":"grounded"}
```

## Run it

From this directory:

```text
python -m unittest discover -s tests -v
python -m evalsplit.cli examples/sample.jsonl --output out --seed demo
```

The command writes `train.jsonl`, `validation.jsonl`, `test.jsonl`, and `report.json` to the output directory. A non-zero exit status means a warning was detected, so CI can choose whether to block the dataset.

The splitter is a preparation aid, not a statistical guarantee. Review the report and domain-specific leakage risks before publishing an evaluation set.
