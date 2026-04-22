from dataclasses import dataclass


@dataclass(frozen=True)
class DailyGoal:
    """
    User's daily study goal in minutes.
    Knows how to convert from hours-per-week (onboarding input).

    Why a Value Object and not a plain int on UserProfile?
    Because the conversion logic (hours → minutes/day) is domain knowledge
    that would otherwise be duplicated across use cases.
    """
    minutes: int

    MIN_MINUTES = 5
    MAX_MINUTES = 480

    def __post_init__(self):
        if self.minutes < self.MIN_MINUTES:
            raise ValueError(f"Minutes {self.minutes} cannot be less than {self.MIN_MINUTES}")

    @classmethod
    def from_hours_per_week(cls, hours: int) -> 'DailyGoal':
        return cls(minutes=round(hours * 60 / 7))

    def __int__(self) -> int:
        return self.minutes
    