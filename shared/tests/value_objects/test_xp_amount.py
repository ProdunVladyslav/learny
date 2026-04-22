"""
Pure unittest — no Django, no DB.
Value objects have the most logic density so they get the most tests.
These run instantly — no transaction overhead.
"""
import unittest

from shared.value_objects import XPAmount


class TestXPAmount(unittest.TestCase):

    # ── Construction ──────────────────────────────────────────────────────────

    def test_valid_value_creates_instance(self):
        xp = XPAmount(value=100)
        self.assertEqual(xp.value, 100)

    def test_zero_is_valid(self):
        xp = XPAmount(value=0)
        self.assertEqual(xp.value, 0)

    def test_max_is_valid(self):
        xp = XPAmount(value=XPAmount.MAX)
        self.assertEqual(xp.value, XPAmount.MAX)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            XPAmount(value=-1)

    def test_exceeds_max_raises(self):
        with self.assertRaises(ValueError):
            XPAmount(value=XPAmount.MAX + 1)

    # ── Addition ──────────────────────────────────────────────────────────────

    def test_add_two_amounts(self):
        result = XPAmount(value=100) + XPAmount(value=200)
        self.assertEqual(result.value, 300)

    def test_add_clamps_at_max(self):
        result = XPAmount(value=9_900) + XPAmount(value=500)
        self.assertEqual(result.value, XPAmount.MAX)

    def test_add_exactly_at_max(self):
        result = XPAmount(value=5_000) + XPAmount(value=5_000)
        self.assertEqual(result.value, XPAmount.MAX)

    def test_add_returns_new_instance(self):
        a = XPAmount(value=100)
        b = XPAmount(value=200)
        result = a + b
        # frozen dataclass — originals unchanged
        self.assertEqual(a.value, 100)
        self.assertEqual(b.value, 200)
        self.assertEqual(result.value, 300)

    # ── Subtraction ───────────────────────────────────────────────────────────

    def test_sub_two_amounts(self):
        result = XPAmount(value=500) - XPAmount(value=200)
        self.assertEqual(result.value, 300)

    def test_sub_clamps_at_zero(self):
        result = XPAmount(value=100) - XPAmount(value=500)
        self.assertEqual(result.value, 0)

    def test_sub_to_exactly_zero(self):
        result = XPAmount(value=100) - XPAmount(value=100)
        self.assertEqual(result.value, 0)

    def test_sub_returns_new_instance(self):
        a = XPAmount(value=500)
        b = XPAmount(value=200)
        result = a - b
        self.assertEqual(a.value, 500)  # unchanged
        self.assertEqual(result.value, 300)

    # ── Int conversion ────────────────────────────────────────────────────────

    def test_int_conversion(self):
        xp = XPAmount(value=150)
        self.assertEqual(int(xp), 150)

    # ── Equality (frozen dataclass gives this for free) ───────────────────────

    def test_equal_values_are_equal(self):
        self.assertEqual(XPAmount(value=100), XPAmount(value=100))

    def test_different_values_are_not_equal(self):
        self.assertNotEqual(XPAmount(value=100), XPAmount(value=200))

    # ── Immutability ──────────────────────────────────────────────────────────

    def test_frozen_cannot_mutate(self):
        xp = XPAmount(value=100)
        with self.assertRaises((AttributeError, TypeError)):
            xp.value = 200  # type: ignore


if __name__ == '__main__':
    unittest.main()