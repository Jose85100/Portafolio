"""Shifted Welford and Chan summaries for finite real scalar streams."""

from dataclasses import dataclass
from math import isfinite
from collections.abc import Iterable


@dataclass(frozen=True)
class Moments:
    n: int = 0
    origin: float = 0.0
    mean_offset: float = 0.0
    m2: float = 0.0

    def push(self, value: float) -> "Moments":
        if not isfinite(value):
            raise ValueError("finite observations required")
        if self.n == 0:
            return Moments(1, value)
        n = self.n + 1
        delta = (value - self.origin) - self.mean_offset
        mean = self.mean_offset + delta / n
        return Moments(
            n, self.origin, mean, self.m2 + delta * ((value - self.origin) - mean)
        )

    def merge(self, other: "Moments") -> "Moments":
        if self.n == 0:
            return other
        if other.n == 0:
            return self
        n = self.n + other.n
        delta = (other.origin - self.origin) + (other.mean_offset - self.mean_offset)
        return Moments(
            n,
            self.origin,
            self.mean_offset + delta * (other.n / n),
            self.m2 + other.m2 + delta * delta * (self.n * other.n / n),
        )

    def variance(self, ddof: int = 0) -> float:
        if ddof not in (0, 1) or self.n <= ddof:
            raise ValueError("ddof must be 0 or 1 with n > ddof")
        return self.m2 / (self.n - ddof)


def summarize(values: Iterable[float]) -> Moments:
    result = Moments()
    for value in values:
        result = result.push(value)
    return result
