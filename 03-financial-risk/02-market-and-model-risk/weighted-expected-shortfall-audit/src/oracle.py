"""Independent CVaR dual linear program: max sum(q_i * loss_i)."""

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import linprog

from src.tail import confidence, distribution


def lp_es(losses: ArrayLike, alpha: float = 0.975, weights: ArrayLike | None = None) -> float:
    mass = confidence(alpha)
    x, p = distribution(losses, weights)
    scale = max(float(np.max(np.abs(x))), 1.0)
    result = linprog(
        -x / scale,
        A_eq=np.ones((1, len(x))),
        b_eq=[1.0],
        bounds=list(zip(np.zeros(len(x)), p / mass, strict=True)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"LP oracle failed: {result.message}")
    return -float(result.fun) * scale
