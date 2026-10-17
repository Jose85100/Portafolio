import numpy as np
from .quantile import radius

def fit(residuals, groups, alpha=0.1):
    r = np.asarray(residuals)
    g = np.asarray(groups)
    return radius(abs(r), alpha), {int(k): radius(abs(r[g == k]), alpha) for k in np.unique(g)}
