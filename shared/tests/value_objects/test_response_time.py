"""
NOTE: There is a bug in the current ResponseTime implementation.

  @property
  def is_fast(self) -> bool:
      return self.ms >= self.FAST_THRESHOLD   # ← WRONG, should be <=

  @property
  def is_slow(self) -> bool:
      return self.ms >= self.SLOW_THRESHOLD   # ← correct

Fast means responding QUICKLY — i.e. ms is LOW (<=), not high (>=).
The tests below document the CORRECT expected behaviour.
Fix the implementation to match.

Corrected implementation:
    @property
    def is_fast(self) -> bool:
        return self.ms <= self.FAST_THRESHOLD   # fast = low ms

    @property
    def is_slow(self) -> bool:
        return self.ms > self.SLOW_THRESHOLD    # slow = high ms

    @property
    def bucket(self) -> str:
        if self.is_fast:
            return 'fast'
        if self.is_slow:
            return 'slow'
        return 'medium'                         # was 'middle' — standardised
"""
import unittest

from shared.value_objects import ResponseTime


class TestResponseTime(unittest.TestCase):

    # ── Construction ──────────────────────────────────────────────────────────

    def test_valid_ms_creates_instance(self):
        rt = ResponseTime(ms=1_000)
        self.assertEqual(rt.ms, 1_000)

    def test_zero_ms_is_valid(self):
        rt = ResponseTime(ms=0)
        self.assertEqual(rt.ms, 0)

    # ── is_fast ───────────────────────────────────────────────────────────────

    def test_below_fast_threshold_is_fast(self):
        """1000ms < 3000ms threshold → fast."""
        rt = ResponseTime(ms=1_000)
        self.assertTrue(rt.is_fast)

    def test_exactly_at_fast_threshold_is_fast(self):
        """3000ms == threshold → fast (boundary)."""
        rt = ResponseTime(ms=ResponseTime.FAST_THRESHOLD)
        self.assertTrue(rt.is_fast)

    def test_above_fast_threshold_not_fast(self):
        """5000ms > 3000ms threshold → not fast."""
        rt = ResponseTime(ms=5_000)
        self.assertFalse(rt.is_fast)

    # ── is_slow ───────────────────────────────────────────────────────────────

    def test_above_slow_threshold_is_slow(self):
        """15000ms > 10000ms threshold → slow."""
        rt = ResponseTime(ms=15_000)
        self.assertTrue(rt.is_slow)

    def test_exactly_at_slow_threshold_is_slow(self):
        rt = ResponseTime(ms=ResponseTime.SLOW_THRESHOLD)
        self.assertTrue(rt.is_slow)

    def test_below_slow_threshold_not_slow(self):
        """5000ms < 10000ms → not slow."""
        rt = ResponseTime(ms=5_000)
        self.assertFalse(rt.is_slow)

    # ── bucket ────────────────────────────────────────────────────────────────

    def test_fast_bucket(self):
        rt = ResponseTime(ms=1_000)
        self.assertEqual(rt.bucket, 'fast')

    def test_medium_bucket(self):
        """Between fast and slow threshold → medium."""
        rt = ResponseTime(ms=5_000)
        self.assertEqual(rt.bucket, 'medium')

    def test_slow_bucket(self):
        rt = ResponseTime(ms=15_000)
        self.assertEqual(rt.bucket, 'slow')

    def test_boundary_fast_threshold_is_fast_bucket(self):
        rt = ResponseTime(ms=ResponseTime.FAST_THRESHOLD)
        self.assertEqual(rt.bucket, 'fast')

    def test_boundary_slow_threshold_is_slow_bucket(self):
        rt = ResponseTime(ms=ResponseTime.SLOW_THRESHOLD)
        self.assertEqual(rt.bucket, 'slow')

    # ── Equality ──────────────────────────────────────────────────────────────

    def test_equal_ms_are_equal(self):
        self.assertEqual(ResponseTime(ms=1_000), ResponseTime(ms=1_000))

    def test_different_ms_not_equal(self):
        self.assertNotEqual(ResponseTime(ms=1_000), ResponseTime(ms=2_000))

    # ── Immutability ──────────────────────────────────────────────────────────

    def test_frozen_cannot_mutate(self):
        from dataclasses import FrozenInstanceError
        rt = ResponseTime(ms=1_000)
        with self.assertRaises(FrozenInstanceError):
            rt.ms = 2_000  # type: ignore


if __name__ == '__main__':
    unittest.main()