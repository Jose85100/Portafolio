"""Online binary scale selection; finite scalar streams, constant state."""

from collections.abc import Iterable
from dataclasses import dataclass
from math import frexp, isfinite, ldexp, sqrt
from src.moments import Moments
from src.scaled import ScaleResult


@dataclass(frozen=True)
class DynamicMoments:
    state: Moments = Moments()
    exponent: int = 0
    initialized: bool = False
    rescales: int = 0
    rounded_to_zero: int = 0

    def push(self, value: float) -> "DynamicMoments":
        if not isfinite(value):
            raise ValueError("finite observations required")
        exponent = frexp(value)[1] if value else self.exponent
        target = max(self.exponent, exponent) if self.initialized else exponent
        state = self.state
        rescales = self.rescales
        lost = self.rounded_to_zero
        if target != self.exponent and state.n:
            shift = self.exponent - target
            origin = ldexp(state.origin, shift)
            offset = ldexp(state.mean_offset, shift)
            m2 = ldexp(state.m2, 2 * shift)
            lost += sum(
                a != 0 and b == 0
                for a, b in [
                    (state.origin, origin),
                    (state.mean_offset, offset),
                    (state.m2, m2),
                ]
            )
            state = Moments(state.n, origin, offset, m2)
            rescales += 1
        normalized = ldexp(value, -target)
        lost += int(value != 0 and normalized == 0)
        return DynamicMoments(
            state.push(normalized),
            target,
            self.initialized or value != 0,
            rescales,
            lost,
        )

    def merge(self, other: "DynamicMoments") -> "DynamicMoments":
        """Merge disjoint summaries after rebasing both to a common unit.

        Counts must describe disjoint observations; overlap is not detectable.
        Floating point reduction is not bitwise associative.
        """
        if self.state.n == 0:
            return other
        if other.state.n == 0:
            return self
        exponents = [item.exponent for item in (self, other) if item.initialized]
        target = max(exponents) if exponents else 0

        def rebase(item: "DynamicMoments") -> tuple[Moments, int, int]:
            shift = item.exponent - target
            old = [item.state.origin, item.state.mean_offset, item.state.m2]
            new = [ldexp(old[0], shift), ldexp(old[1], shift), ldexp(old[2], 2 * shift)]
            lost = sum(a != 0 and b == 0 for a, b in zip(old, new))
            return (Moments(item.state.n, *new), int(shift != 0), lost)

        left, left_rescales, left_lost = rebase(self)
        right, right_rescales, right_lost = rebase(other)
        return DynamicMoments(
            left.merge(right),
            target,
            self.initialized or other.initialized,
            self.rescales + other.rescales + left_rescales + right_rescales,
            self.rounded_to_zero + other.rounded_to_zero + left_lost + right_lost,
        )

    def result(self, ddof: int = 0) -> ScaleResult:
        variance = self.state.variance(ddof)
        try:
            std = ldexp(sqrt(variance), self.exponent)
        except OverflowError:
            return ScaleResult(self.state.n, self.exponent, "std_overflow")
        if std == 0 and variance > 0:
            return ScaleResult(self.state.n, self.exponent, "std_underflow")
        try:
            physical = ldexp(variance, 2 * self.exponent)
        except OverflowError:
            return ScaleResult(
                self.state.n, self.exponent, "variance_overflow", std=std
            )
        status = "variance_underflow" if physical == 0 and variance > 0 else "ok"
        return ScaleResult(self.state.n, self.exponent, status, physical, std)


def dynamic_moments(values: Iterable[float], ddof: int = 0) -> ScaleResult:
    state = DynamicMoments()
    for value in values:
        state = state.push(value)
    return state.result(ddof)
