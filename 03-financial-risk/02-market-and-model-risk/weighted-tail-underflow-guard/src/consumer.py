"""Audit-preserving decision boundary; not a forecast accuracy guarantee."""

import json
from fractions import Fraction
from typing import Any, Literal

from numpy.typing import ArrayLike

from src.guard import TailUnderflowError, guarded_tail


def decide(
    losses: ArrayLike,
    threshold: str,
    alpha: float = 0.975,
    weights: ArrayLike | None = None,
    policy: Literal["exact", "raise"] = "exact",
    max_exact_scenarios: int = 4096,
) -> dict[str, Any]:
    """Return strict ES > threshold, or a rejection with no numerical decision.

    Threshold is an exact decimal or rational STRING, never a coerced float.
    Fallback compares retained Fraction; fast path compares its binary64 ES
    exactly to the threshold, without claiming the ES itself is exact.
    Invalid inputs remain programmer errors (ValueError), not accepted packets.
    """
    if not isinstance(threshold, str):
        raise ValueError("threshold must be a finite decimal or rational string")
    try:
        limit = Fraction(threshold)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("invalid finite threshold") from error
    common: dict[str, Any] = {
        "schema": "weighted-es-decision/v1",
        "threshold": {"numerator": str(limit.numerator), "denominator": str(limit.denominator)},
        "comparison": ">",
    }
    try:
        result = guarded_tail(losses, alpha, weights, policy, max_exact_scenarios)
    except TailUnderflowError as error:
        return {**common, "status": "rejected", "breach": None, "reason": str(error)}
    value = result.exact_es if result.exact_es is not None else Fraction(result.es)
    return {
        **common,
        "status": "accepted",
        "breach": value > limit,
        "comparison_basis": "exact-input-rational" if result.exact_es is not None else "binary64-output",
        "es_float": result.es,
        "es_rational": {"numerator": str(value.numerator), "denominator": str(value.denominator)},
        "output_rounds_to_zero": result.output_rounds_to_zero,
        "backend": result.backend,
        "fallback_reason": result.fallback_reason,
    }


def encode(packet: dict[str, Any]) -> str:
    """Strict JSON; integer strings survive consumers with binary64 numbers."""
    return json.dumps(packet, allow_nan=False, sort_keys=True, separators=(",", ":"))
