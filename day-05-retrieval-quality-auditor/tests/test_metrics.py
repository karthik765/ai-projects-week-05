import unittest

from retrieval_audit.metrics import audit_records, compare_audits
from retrieval_audit.models import RetrievalCase


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.cases = [
            RetrievalCase("q1", ("a",), ("x", "a"), ("a",)),
            RetrievalCase("q2", ("b", "c"), ("b", "z"), ("b",)),
            RetrievalCase("q3", ("d",), ("x", "y")),
        ]

    def test_rank_metrics_and_misses(self):
        report = audit_records(self.cases)
        self.assertEqual(report["cases"], 3)
        self.assertAlmostEqual(report["mrr"], (0.5 + 1 + 0) / 3, places=4)
        self.assertEqual(report["missed_query_ids"], ["q3"])
        self.assertEqual(report["k"]["1"]["hit_rate"], 0.3333)

    def test_citation_coverage_ignores_non_relevant_citations(self):
        report = audit_records(self.cases)
        self.assertAlmostEqual(report["citation_coverage"], 0.75, places=4)

    def test_duplicate_retrieval_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            RetrievalCase.from_dict({"query_id": "q", "relevant_ids": ["a"], "retrieved_ids": ["a", "a"]}, 4)

    def test_regression_warning_uses_tolerance(self):
        self.assertEqual(compare_audits({"mrr": 0.8, "mean_recall": 0.7}, {"mrr": 0.7, "mean_recall": 0.7}), ["mrr regressed from 0.8000 to 0.7000"])


if __name__ == "__main__":
    unittest.main()
