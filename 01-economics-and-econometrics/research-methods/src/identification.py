"""Small, auditable OLS/IV laboratory for one regressor and one instrument.

The routines estimate point coefficients only. No causal claim follows from
numerical execution: exclusion and conditional exogeneity are assumptions.
"""
from math import isfinite
from random import Random


def _series(*series):
    arrays = [tuple(float(v) for v in s) for s in series]
    if not arrays or len(arrays[0]) < 3 or any(len(s) != len(arrays[0]) for s in arrays):
        raise ValueError("aligned arrays with at least 3 observations required")
    if not all(isfinite(v) for s in arrays for v in s):
        raise ValueError("nonfinite observation")
    return arrays


def covariance(x, y):
    """Population-normalized sample covariance; denominator cancels in ratios."""
    x, y = _series(x, y)
    mx, my = sum(x)/len(x), sum(y)/len(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/len(x)


def ols_slope(y, x):
    """Intercept-inclusive bivariate OLS slope."""
    y, x = _series(y,x)
    var = covariance(x,x)
    if var <= 1e-14:
        raise ValueError("regressor has zero or near-zero variance")
    return covariance(x,y)/var


def iv_slope(y, x, z):
    """Just-identified IV/Wald slope with intercept and no controls."""
    y,x,z = _series(y,x,z)
    denominator=covariance(z,x)
    if abs(denominator) <= 1e-14:
        raise ValueError("instrument has zero or near-zero first-stage covariance")
    return covariance(z,y)/denominator


def generate_endogenous_dgp(n=3000, beta=-1.5, endogeneity=.8,
                            instrument_strength=1.0, seed=17):
    """y=beta*x+u, x=strength*z+endogeneity*u+v.

    Independent standard normal z,u,v. Under exclusion and relevance, IV
    targets beta; OLS generally does not. Returns a deterministic synthetic DGP.
    """
    if n < 3 or not all(isfinite(v) for v in (beta,endogeneity,instrument_strength)):
        raise ValueError("invalid DGP configuration")
    rng=Random(seed)
    y,x,z=[],[],[]
    for _ in range(n):
        zi,ui,vi=(rng.gauss(0,1) for _ in range(3))
        xi=instrument_strength*zi+endogeneity*ui+vi
        z.append(zi);x.append(xi);y.append(beta*xi+ui)
    return {"y":y,"x":x,"z":z,"true_beta":beta}


def analytical_ols_probability_limit(beta, endogeneity, instrument_strength):
    """Plim OLS for the specified unit-variance independent Gaussian DGP."""
    return beta + endogeneity/(instrument_strength**2+endogeneity**2+1)
