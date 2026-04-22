from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class XPAmount:
    value: int

    MAX: ClassVar[int] = 10_000

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(f"XP cannot be negative, got {self.value}")
        if self.value > self.MAX:
            raise ValueError(f"XP cannot exceed {self.MAX}, got {self.value}")

    def __add__(self, other: 'XPAmount') -> 'XPAmount':
        return XPAmount(min(self.value + other.value, self.MAX))

    def __sub__(self, other: 'XPAmount') -> 'XPAmount':
        return XPAmount(max(self.value - other.value, 0))

    def __int__(self) -> int:
        return self.value