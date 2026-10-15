import json
import unittest

from trace_analyzer.compare import compare
from trace_analyzer.metrics import analyze, percentile
from trace_analyzer.parser import read_jsonl


class TraceAnalyzerTests(unittest.TestCase):
    def test_parser_reports_bad_lines_and_normalizes_records(self):
        records, issues = read_jsonl(['{"request_id":"a","model":"m","latency_ms":10,"prompt_tokens":2,"completion_tokens":3}', "not json"])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].total_tokens, 5)
        self.assertEqual(len(issues), 1)

    def test_percentile_interpolates(self):
        self.assertEqual(percentile([10, 20, 40, 80], 50), 30.0)

    def test_analysis_counts_status_tokens_and_slowest(self):
        records, _ = read_jsonl([
            json.dumps({"request_id": "a", "model": "m", "latency_ms": 10, "prompt_tokens": 2, "completion_tokens": 3}),
            json.dumps({"request_id": "b", "model": "m2", "latency_ms": 50, "prompt_tokens": 4, "completion_tokens": 1, "status": "error"}),
        ])
        report = analyze(records)
        self.assertEqual(report["requests"], 2)
        self.assertEqual(report["failures"], 1)
        self.assertEqual(report["tokens"]["total"], 10)
        self.assertEqual(report["slowest"][0]["request_id"], "b")

    def test_compare_flags_latency_and_failure_regressions(self):
        base = analyze(read_jsonl(['{"request_id":"a","model":"m","latency_ms":10,"prompt_tokens":1,"completion_tokens":1}'])[0])
        candidate = analyze(read_jsonl(['{"request_id":"a","model":"m","latency_ms":100,"prompt_tokens":1,"completion_tokens":1,"status":"error"}'])[0])
        result = compare(base, candidate)
        self.assertTrue(result["regression"])
        self.assertEqual(len(result["warnings"]), 2)

    def test_empty_input_is_safe(self):
        report = analyze([])
        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["latency_ms"]["p95"], 0.0)


if __name__ == "__main__":
    unittest.main()
