"""Finite-sample split conformal quantile."""
import math
import numpy as np

def radius(scores, alpha=0.1):
    s = np.asarray(scores, dtype=float)
    if s.ndim != 1 or len(s) == 0 or not np.isfinite(s).all() or np.any(s < 0):
        raise ValueError("invalid scores")
    if not 0 < alpha < 1:
        raise ValueError("invalid alpha")
    k = math.ceil((len(s)+1)*(1-alpha))
    return float(np.partition(s, k-1)[k-1]) if k <= len(s) else float("inf")
