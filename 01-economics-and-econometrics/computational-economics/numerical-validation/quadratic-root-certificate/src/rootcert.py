"""Exact rational enclosures for real roots of quadratic regime equations."""

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt


@dataclass(frozen=True)
class Interval:
    lower: Fraction
    upper: Fraction
    multiplicity: int

    @property
    def width(self) -> Fraction:
        return self.upper - self.lower

    @property
    def midpoint(self) -> Fraction:
        return (self.lower + self.upper) / 2


def _sqrt_enclosure(value: Fraction, decimal_digits: int) -> tuple[Fraction, Fraction]:
    if value < 0 or not 1 <= decimal_digits <= 200:
        raise ValueError("Nonnegative value and 1..200 decimal digits required")
    scale = 10**decimal_digits
    scaled_floor = value.numerator * scale * scale // value.denominator
    integer = isqrt(scaled_floor)
    lower = Fraction(integer, scale)
    if integer * integer * value.denominator == value.numerator * scale * scale:
        return lower, lower
    return lower, Fraction(integer + 1, scale)


def isolate_quadratic(
    a: Fraction,
    b: Fraction,
    c: Fraction,
    *,
    decimal_digits: int = 18,
) -> tuple[Interval, ...]:
    """Enclose every real root of ``a*x^2+b*x+c`` using exact rationals.

    The certificate is specialised to degree two.  Its guarantee concerns the
    polynomial only; economic regime inequalities must be checked separately.
    """
    if a == 0:
        raise ValueError("A nonzero quadratic coefficient is required")
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return ()
    denominator = 2 * a
    if discriminant == 0:
        root = -b / denominator
        return (Interval(root, root, 2),)
    sqrt_lower, sqrt_upper = _sqrt_enclosure(discriminant, decimal_digits)
    bounds: list[Interval] = []
    for sign in (-1, 1):
        numerators = (-b + sign * sqrt_lower, -b + sign * sqrt_upper)
        candidates = tuple(value / denominator for value in numerators)
        bounds.append(Interval(min(candidates), max(candidates), 1))
    return tuple(sorted(bounds, key=lambda interval: interval.lower))


def evaluate(a: Fraction, b: Fraction, c: Fraction, x: Fraction) -> Fraction:
    return a * x * x + b * x + c


def verify_certificate(
    a: Fraction, b: Fraction, c: Fraction, intervals: tuple[Interval, ...]
) -> bool:
    """Verify enclosure shape and exact sign/multiplicity conditions."""
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return not intervals
    if discriminant == 0:
        return (
            len(intervals) == 1
            and intervals[0].multiplicity == 2
            and intervals[0].lower == intervals[0].upper == -b / (2 * a)
        )
    if len(intervals) != 2 or intervals[0].upper >= intervals[1].lower:
        return False
    for interval in intervals:
        if interval.multiplicity != 1 or interval.lower > interval.upper:
            return False
        left = evaluate(a, b, c, interval.lower)
        right = evaluate(a, b, c, interval.upper)
        if left * right > 0:
            return False
    return True


def select_in_domain(
    intervals: tuple[Interval, ...], lower: Fraction, upper: Fraction
) -> tuple[Interval, ...]:
    """Retain certificates wholly contained in an economic regime domain."""
    if lower > upper:
        raise ValueError("Ordered domain required")
    return tuple(i for i in intervals if lower <= i.lower and i.upper <= upper)
