import unittest

from context_planner import Message, plan_context
from context_planner.tokenizer import estimate_tokens


class PlannerTests(unittest.TestCase):
    def test_pinned_and_system_messages_are_kept(self):
        messages = [
            Message("system", "rules"),
            Message("user", "old detail " * 30),
            Message("user", "must keep", pinned=True),
        ]
        plan = plan_context(messages, estimate_tokens("rules") + estimate_tokens("must keep"))
        self.assertEqual(plan.selected, [0, 2])
        self.assertEqual([item.index for item in plan.dropped], [1])

    def test_priority_fills_remaining_budget(self):
        messages = [Message("user", "low"), Message("user", "high", priority=4)]
        plan = plan_context(messages, estimate_tokens("high"))
        self.assertEqual(plan.selected, [1])

    def test_original_order_is_preserved(self):
        messages = [Message("user", "a"), Message("user", "b", priority=2), Message("user", "c " * 10, priority=1)]
        plan = plan_context(messages, estimate_tokens("a") + estimate_tokens("b"))
        self.assertEqual(plan.selected, [0, 1])

    def test_required_overflow_is_reported(self):
        plan = plan_context([Message("system", "a" * 100)], 1)
        self.assertEqual(plan.selected, [0])
        self.assertTrue(plan.warnings)

    def test_invalid_budget_fails(self):
        with self.assertRaises(ValueError):
            plan_context([], 0)


if __name__ == "__main__":
    unittest.main()
