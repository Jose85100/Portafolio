"""Historical, Gaussian and fitted-t tail demo; returns are decimal observations.

The default historical API uses an empirical inverse-CDF VaR and fractional-mass
ES. A named legacy comparator is retained for the versioned definition audit.
"""
from math import ceil, fsum
import numpy as np
from scipy import stats


def _validate(r, nivel):
    observations = np.asarray(r, dtype=float)
    if observations.ndim != 1 or len(observations) < 2 or not np.isfinite(observations).all():
        raise ValueError("At least two finite returns required")
    if not np.isfinite(nivel) or not 0 < nivel < 1:
        raise ValueError("Confidence level must be in (0,1)")
    return observations


def historico(r, nivel):
    """Losses = -returns; include only the required fraction of the VaR atom."""
    losses = np.sort(-_validate(r, nivel))
    n = len(losses); mass = n * (1 - nivel)
    whole = int(mass); fractional = mass-whole
    terms = [float(x)/mass for x in losses[-whole:]] if whole else []
    if fractional:
        terms.append(float(losses[-whole-1])*(fractional/mass))
    try:
        es = fsum(terms)
    except OverflowError as error:
        raise ArithmeticError("ES accumulation overflow") from error
    if not np.isfinite(es):raise ArithmeticError("Nonfinite ES")
    return float(losses[max(0,min(n-1,ceil(nivel*n)-1))]),es


def historico_legacy_conditional(r, nivel):
    """Old threshold-conditioned mean: deliberately not the default ES contract."""
    var = -np.quantile(r, 1 - nivel)
    es = -r[r <= -var].mean()
    return var, es


def normal(r, nivel):
    r = _validate(r, nivel)
    mu, sd = r.mean(), r.std(ddof=1)
    z = stats.norm.ppf(1 - nivel)
    return -(mu + sd*z), -(mu-sd*stats.norm.pdf(z)/(1-nivel))


def t_student(r, nivel, seed=17):
    r = _validate(r, nivel)
    df, loc, scale = stats.t.fit(r)
    # Fitted predictive distribution, not an empirical estimate on the same n.
    draws = stats.t.rvs(df,loc,scale,size=400_000,random_state=np.random.default_rng(seed))
    return historico(draws,nivel)


def main():
    rng=np.random.default_rng(17);degrees=4;value=1_000_000
    returns=stats.t.rvs(degrees,size=2500,random_state=rng)*.01/np.sqrt(degrees/(degrees-2))
    print(f"Valor del portafolio: {value:,.0f} | observaciones: {len(returns)}")
    print(f"{'nivel':>6} {'metodo':>12} {'VaR':>12} {'ES':>12}")
    for level in (.95,.99):
        for name,method in (("historico",historico),("normal",normal),("t-student",t_student)):
            var,es=method(returns,level)
            print(f"{level:>6.2f} {name:>12} {var*value:>12,.0f} {es*value:>12,.0f}")


if __name__ == '__main__':main()
