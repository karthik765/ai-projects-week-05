import unittest

from tool_policy import Policy, PolicyChecker, ToolCall


class PolicyCheckerTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy(
            allowed_tools=["search", "send_email"],
            blocked_tools=["delete_records"],
            blocked_argument_keys=["password", "private_key"],
            require_confirmation_for=["send_email"],
            max_calls=2,
        )

    def test_allowed_call_is_allowed(self):
        report = PolicyChecker(self.policy).check([ToolCall("search", {"query": "docs"})])
        self.assertEqual(report["status"], "allow")
        self.assertEqual(report["risk_score"], 0)

    def test_confirmation_is_review(self):
        report = PolicyChecker(self.policy).check([ToolCall("send_email", {"to": "a@example.com"})])
        self.assertEqual(report["status"], "review")
        self.assertEqual(report["findings"][0]["code"], "CONFIRMATION_REQUIRED")

    def test_unknown_and_blocked_tools_are_denied(self):
        report = PolicyChecker(self.policy).check([ToolCall("shell", {}), ToolCall("delete_records", {})])
        self.assertEqual(report["status"], "deny")
        self.assertEqual({f["code"] for f in report["findings"]}, {"UNKNOWN_TOOL", "BLOCKED_TOOL"})

    def test_blocked_argument_is_explained(self):
        report = PolicyChecker(self.policy).check([ToolCall("search", {"query": "x", "password": "secret"})])
        finding = report["findings"][0]
        self.assertEqual(finding["code"], "BLOCKED_ARGUMENT")
        self.assertEqual(finding["evidence"], "password")

    def test_call_limit_is_global(self):
        report = PolicyChecker(self.policy).check([ToolCall("search"), ToolCall("search"), ToolCall("search")])
        self.assertEqual(report["status"], "deny")
        self.assertIn("CALL_LIMIT", {f["code"] for f in report["findings"]})

    def test_policy_from_dict_rejects_bad_limit(self):
        with self.assertRaises(ValueError):
            Policy.from_dict({"allowed_tools": [], "max_calls": 0})


if __name__ == "__main__":
    unittest.main()
