"""Local MOMENTS_V1 transport: normalized binary64 summaries, not observations."""

from math import isfinite
from src.dynamic import DynamicMoments
from src.moments import Moments

MAX_COUNT = 2**53 - 1


def validate(state: DynamicMoments) -> None:
    s = state.state
    if type(s.n) is not int or not 0 <= s.n <= MAX_COUNT:
        raise ValueError("count outside exact binary64 integer domain")
    if type(state.exponent) is not int or not -1073 <= state.exponent <= 1024:
        raise ValueError("exponent outside binary64 normalization domain")
    if not all(
        type(x) is float and isfinite(x) for x in [s.origin, s.mean_offset, s.m2]
    ):
        raise ValueError("finite state required")
    if abs(s.origin) > 1 or abs(s.mean_offset) > 2 or not 0 <= s.m2 <= 4 * s.n:
        raise ValueError("normalized structural bounds violated")
    if (not state.initialized or s.n == 0) and (
        state.initialized or state.exponent != 0 or any([s.origin, s.mean_offset, s.m2])
    ):
        raise ValueError("zero or empty summary inconsistent")


def export_state(state: DynamicMoments) -> str:
    """Exact hex doubles; historical diagnostics deliberately not transported."""
    validate(state)
    s = state.state
    return f"MOMENTS_V1 {s.n} {state.exponent} {s.origin.hex()} {s.mean_offset.hex()} {s.m2.hex()} {int(state.initialized)}"


def import_state(text: str) -> DynamicMoments:
    fields = text.split()
    if len(fields) != 7 or fields[0] != "MOMENTS_V1" or fields[6] not in {"0", "1"}:
        raise ValueError("invalid MOMENTS_V1 fields")
    if any(not word.lstrip("+-").isdigit() for word in fields[1:3]):
        raise ValueError("integer fields required")
    if any("0x" not in word or "p" not in word for word in fields[3:6]):
        raise ValueError("hexadecimal floating fields required")
    state = DynamicMoments(
        Moments(int(fields[1]), *(float.fromhex(x) for x in fields[3:6])),
        int(fields[2]),
        fields[6] == "1",
    )
    validate(state)
    return state
