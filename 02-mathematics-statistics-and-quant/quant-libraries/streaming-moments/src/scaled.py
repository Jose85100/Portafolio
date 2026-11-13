"""Externally scaled view of the existing29 moments kernel; no auto scale inference."""

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite, ldexp, sqrt
from src.moments import Moments


@dataclass(frozen=True)
class ScaleResult:
    n: int
    exponent: int
    status: str
    variance: float | None = None
    std: float | None = None


def scaled_moments(
    values: Iterable[float], exponent: int, ddof: int = 0
) -> ScaleResult:
    """Return physical-unit variance/SD or explicit range failure. State O(1).

    Normalized nonzero observations must lie in [2^-400,2^400]. This is
    a conservative operational domain, not a universal floating error bound.
    """
    if type(exponent) is not int or not -1074 <= exponent <= 1023:
        raise ValueError("integer exponent in [-1074,1023] required")
    if ddof not in (0, 1):
        raise ValueError("ddof must be 0 or 1")
    state = Moments()
    for value in values:
        if not isfinite(value):
            raise ValueError("finite observations required")
        try:
            y = ldexp(value, -exponent)
        except OverflowError:
            return ScaleResult(state.n, exponent, "normalization_failure")
        if not isfinite(y) or (
            value != 0 and not ldexp(1.0, -400) <= abs(y) <= ldexp(1.0, 400)
        ):
            return ScaleResult(state.n, exponent, "normalization_failure")
        state = state.push(y)
        if (
            not all(isfinite(z) for z in [state.origin, state.mean_offset, state.m2])
            or state.m2 < 0
        ):
            return ScaleResult(state.n, exponent, "normalization_failure")
    variance_scaled = state.variance(ddof)
    try:
        std = ldexp(sqrt(variance_scaled), exponent)
    except OverflowError:
        return ScaleResult(state.n, exponent, "std_overflow")
    if not isfinite(std):
        return ScaleResult(state.n, exponent, "std_overflow")
    try:
        variance = ldexp(variance_scaled, 2 * exponent)
    except OverflowError:
        return ScaleResult(state.n, exponent, "variance_overflow", std=std)
    if variance == 0 and variance_scaled > 0:
        return ScaleResult(state.n, exponent, "variance_underflow", std=std)
    return ScaleResult(state.n, exponent, "ok", variance, std)
