"""Already credit-impaired non-POCI assets: gross carrying amount minus recovery PV."""

import numpy as np
from numpy.typing import ArrayLike, NDArray


def shortfall(gross: ArrayLike, recoveries: ArrayLike, years: ArrayLike, eir: float) -> NDArray[np.float64]:
    """Batch ECL for known default state with nonnegative net recoveries.

    gross: n; recoveries: n x periods; years: periods from reporting date.
    No new-default PD multiplier. Original EIR is supplied, not estimated.
    Scope restricts nominal recovery totals <= gross and nonnegative EIR.
    Stable decomposition: unrecovered principal + loss from delayed recovery.
    """
    g = np.asarray(gross, dtype=np.float64)
    c = np.asarray(recoveries, dtype=np.float64)
    t = np.asarray(years, dtype=np.float64)
    if g.ndim != 1 or not g.size or np.any(~np.isfinite(g)) or np.any(g < 0):
        raise ValueError("gross must be a nonempty finite nonnegative vector")
    if t.ndim != 1 or not t.size or np.any(~np.isfinite(t)) or np.any(t < 0):
        raise ValueError("years must be a nonempty finite nonnegative vector")
    if c.shape != (g.size, t.size) or np.any(~np.isfinite(c)) or np.any(c < 0):
        raise ValueError("recoveries must be finite nonnegative n x periods")
    if not np.isfinite(eir) or eir < 0:
        raise ValueError("eir must be finite and nonnegative")
    total = c.sum(axis=1)
    if np.any(~np.isfinite(total)) or np.any(total > g):
        raise ValueError("nominal recoveries cannot exceed gross in this prototype")
    delay_loss = -np.expm1(-np.log1p(eir) * t)
    return (g - total) + (c * delay_loss).sum(axis=1)


def scenario_shortfall(
    gross: ArrayLike, recoveries: ArrayLike, years: ArrayLike, eir: float, weights: ArrayLike
) -> NDArray[np.float64]:
    """Scenario x loan x period cash flows, one shared EIR and fixed weights."""
    c = np.asarray(recoveries, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    if c.ndim != 3 or w.shape != (c.shape[0],) or not w.size:
        raise ValueError("expected scenario x loan x period and matching weights")
    if np.any(~np.isfinite(w)) or np.any(w < 0) or not np.isclose(w.sum(), 1, atol=1e-12, rtol=0):
        raise ValueError("scenario weights must be finite nonnegative and sum to one")
    return np.stack([shortfall(gross, case, years, eir) for case in c]).T @ w
