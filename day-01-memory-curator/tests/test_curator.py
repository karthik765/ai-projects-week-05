import unittest

from memory_curator.curator import curate
from memory_curator.models import Turn


class CuratorTests(unittest.TestCase):
    def test_extracts_preference_and_task(self):
        report = curate([Turn("1", "user", "I prefer concise weekly reports."), Turn("2", "user", "I need to review the draft.")])
        self.assertEqual(["preference", "task"], [item.kind for item in report.memories])

    def test_masks_sensitive_values(self):
        report = curate([Turn("1", "user", "Remember that my email is jane@example.com.")])
        self.assertIn("[email]", report.memories[0].value)
        self.assertNotIn("jane@example.com", report.memories[0].evidence)

    def test_ignores_assistant_claims(self):
        report = curate([Turn("1", "assistant", "I prefer detailed answers.")])
        self.assertEqual([], report.memories)
        self.assertEqual(1, report.ignored_turns)

    def test_merges_repeated_fact(self):
        report = curate([Turn("1", "user", "Remember that I work remotely."), Turn("2", "user", "Remember that I work remotely!")])
        self.assertEqual(1, len(report.memories))
        self.assertEqual(["1", "2"], report.memories[0].evidence_turns)

    def test_reports_conflicting_fact_values(self):
        report = curate([Turn("1", "user", "My timezone is Eastern."), Turn("2", "user", "My timezone is Pacific.")])
        self.assertEqual(1, len(report.conflicts))
        self.assertEqual({"Eastern", "Pacific"}, set(report.conflicts[0]["values"]))

    def test_weak_statements_get_lower_confidence(self):
        report = curate([Turn("1", "user", "I am a designer.")])
        self.assertLess(report.memories[0].confidence, 0.9)


if __name__ == "__main__":
    unittest.main()
