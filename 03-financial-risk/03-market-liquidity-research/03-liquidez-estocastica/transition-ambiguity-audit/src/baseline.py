"""Reuse the unchanged forward DP27 as independent nominal/static-matrix comparator."""

import importlib.util
import sys
from collections.abc import Sequence
from pathlib import Path

PATH = (
    Path(__file__).resolve().parents[2]
    / "markov-first-breach-audit"
    / "src"
    / "breach.py"
)
SPEC = importlib.util.spec_from_file_location("liquidity_forward_dp27", PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError("sibling DP27 unavailable")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def nominal(
    cash: int,
    horizon: int,
    stress_probabilities: Sequence[float],
    initial: Sequence[float] = (0.8, 0.2),
) -> float:
    result = MODULE.first_breach(
        cash, horizon, [1, -2], [[1 - p, p] for p in stress_probabilities], initial
    )
    return float(result.breach_probability)
