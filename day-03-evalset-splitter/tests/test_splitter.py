import unittest

from evalsplit.models import SplitConfig
from evalsplit.splitter import split_records


class SplitterTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": f"{label}-{i}", "text": f"Example {label} {i}", "label": label}
            for label in ("good", "bad") for i in range(10)
        ]

    def test_same_seed_is_reproducible(self):
        config = SplitConfig(0.6, 0.2, 0.2, "fixed")
        first = split_records(self.records, config)
        second = split_records(self.records, config)
        self.assertEqual(first.splits, second.splits)
        self.assertEqual(first.report["counts"], {"train": 12, "validation": 4, "test": 4})

    def test_label_stratification(self):
        result = split_records(self.records, SplitConfig(0.5, 0.25, 0.25, "labels"))
        for values in result.splits.values():
            self.assertEqual(len({r["label"] for r in values}), 2)

    def test_duplicates_are_reported_and_cross_split_leakage_is_detected(self):
        records = [{"id": "one", "text": "Same answer"}, {"id": "two", "text": " same   answer "}]
        result = split_records(records, SplitConfig(0.5, 0.0, 0.5, "dupes"))
        self.assertEqual(result.report["normalized_duplicate_groups"], 1)
        self.assertTrue(any("duplicate" in warning for warning in result.warnings))

    def test_invalid_ratios_are_rejected(self):
        with self.assertRaises(ValueError):
            SplitConfig(0.5, 0.5, 0.2)


if __name__ == "__main__":
    unittest.main()
