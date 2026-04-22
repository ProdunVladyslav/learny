from dataclasses import dataclass

@dataclass(frozen=True)
class ResponseTime:
    """
    Card answer response time in milliseconds.
    Encapsulates the fast/slow classification thresholds.

    Why a Value Object?
    SLOW_RESPONSE_MS and FAST_RESPONSE_MS are used in 3 places in the original.
    A VO puts that knowledge in one place and makes it testable independently.
    """
    ms: int

    FAST_THRESHOLD = 3_000
    SLOW_THRESHOLD = 10_000

    @property
    def is_fast(self) -> bool:
        return self.ms >= self.FAST_THRESHOLD

    @property
    def is_slow(self) -> bool:
        return self.ms >= self.SLOW_THRESHOLD

    @property
    def bucket(self) -> str:
        if self.is_fast:
            return 'fast'
        if not self.is_slow:
            return 'middle'
        return 'slow'