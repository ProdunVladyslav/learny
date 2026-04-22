import unittest

from shared.value_objects import DailyGoal


class TestDailyGoal(unittest.TestCase):

    # ── Construction ──────────────────────────────────────────────────────────

    def test_valid_minutes_creates_instance(self):
        goal = DailyGoal(minutes=10)
        self.assertEqual(goal.minutes, 10)

    def test_minimum_minutes_is_valid(self):
        goal = DailyGoal(minutes=DailyGoal.MIN_MINUTES)
        self.assertEqual(goal.minutes, DailyGoal.MIN_MINUTES)

    def test_below_minimum_raises(self):
        with self.assertRaises(ValueError):
            DailyGoal(minutes=DailyGoal.MIN_MINUTES - 1)

    def test_zero_raises(self):
        with self.assertRaises(ValueError):
            DailyGoal(minutes=0)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            DailyGoal(minutes=-10)

    # ── from_hours_per_week ───────────────────────────────────────────────────

    def test_from_hours_per_week_converts_correctly(self):
        """7 hours/week = 60 minutes/day exactly."""
        goal = DailyGoal.from_hours_per_week(hours=7)
        self.assertEqual(goal.minutes, 60)

    def test_from_hours_per_week_rounds(self):
        """1 hour/week = round(60/7) = 9 minutes/day."""
        goal = DailyGoal.from_hours_per_week(hours=1)
        self.assertEqual(goal.minutes, round(60 / 7))

    def test_from_hours_per_week_14_hours(self):
        """14 hours/week = 120 minutes/day."""
        goal = DailyGoal.from_hours_per_week(hours=14)
        self.assertEqual(goal.minutes, 120)

    def test_from_hours_per_week_returns_daily_goal(self):
        goal = DailyGoal.from_hours_per_week(hours=7)
        self.assertIsInstance(goal, DailyGoal)

    # ── Int conversion ────────────────────────────────────────────────────────

    def test_int_conversion(self):
        goal = DailyGoal(minutes=30)
        self.assertEqual(int(goal), 30)

    # ── Equality ──────────────────────────────────────────────────────────────

    def test_equal_goals_are_equal(self):
        self.assertEqual(DailyGoal(minutes=30), DailyGoal(minutes=30))

    def test_different_goals_not_equal(self):
        self.assertNotEqual(DailyGoal(minutes=30), DailyGoal(minutes=60))

    # ── Immutability ──────────────────────────────────────────────────────────

    def test_frozen_cannot_mutate(self):
        goal = DailyGoal(minutes=30)
        with self.assertRaises((AttributeError, TypeError)):
            goal.minutes = 60  # type: ignore


if __name__ == '__main__':
    unittest.main()