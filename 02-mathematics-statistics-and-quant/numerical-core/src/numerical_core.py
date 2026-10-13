"""Auditable numerical baselines. Python standard library only; no production claims."""
from math import ceil, exp, isfinite, log, sqrt
from random import Random
from statistics import NormalDist, mean


def _finite(values):
    v = tuple(float(x) for x in values)
    if not v or not all(isfinite(x) for x in v):
        raise ValueError("expected nonempty finite observations")
    return v


def quantile(values, alpha):
    """Empirical nearest-rank quantile (non-interpolating)."""
    v = sorted(_finite(values))
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0,1]")
    return v[ceil(alpha * len(v)) - 1]


def expected_shortfall(values, alpha):
    """Discrete tail average from nearest-rank VaR index (ties included by rank)."""
    v = sorted(_finite(values))
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0,1)")
    k = ceil(alpha * len(v)) - 1
    return sum(v[k:]) / (len(v) - k)


def wasserstein_1d(x, y):
    """Exact empirical W1 for equally weighted samples with equal sample sizes."""
    a, b = sorted(_finite(x)), sorted(_finite(y))
    if len(a) != len(b):
        raise ValueError("equal sample sizes required for this baseline")
    return mean(abs(u - v) for u, v in zip(a, b))


def kl_bernoulli(p, q):
    """KL(Bernoulli(p) || Bernoulli(q)), with boundary conventions."""
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise ValueError("probabilities must lie in [0,1]")
    if (p > 0 and q == 0) or (p < 1 and q == 1):
        return float("inf")
    left = p * log(p / q) if p else 0.0
    right = (1-p) * log((1-p)/(1-q)) if p < 1 else 0.0
    return left + right


def euler_maruyama_gbm(s0, mu, sigma, maturity, steps, paths=1000, seed=0):
    """GBM Euler-Maruyama terminal sample. May turn negative for coarse steps."""
    if not (isfinite(s0) and s0 > 0 and isfinite(mu) and isfinite(sigma) and sigma >= 0
            and isfinite(maturity) and maturity >= 0 and steps > 0 and paths > 0):
        raise ValueError("invalid SDE parameters")
    rng = Random(seed)
    dt = maturity / steps
    scale = sigma * sqrt(dt)
    terminals = []
    for _ in range(paths):
        x = s0
        for _ in range(steps):
            x *= 1 + mu * dt + scale * rng.gauss(0, 1)
        terminals.append(x)
    return terminals


def gbm_exact_terminal(s0, mu, sigma, maturity, paths=1000, seed=0):
    """Exact GBM marginal for benchmarking discretization bias."""
    if not (s0 > 0 and sigma >= 0 and maturity >= 0 and paths > 0):
        raise ValueError("invalid GBM parameters")
    rng = Random(seed)
    return [s0 * exp((mu - 0.5*sigma*sigma)*maturity
                     + sigma*sqrt(maturity)*rng.gauss(0,1)) for _ in range(paths)]


def bs_call(s0, strike, rate, sigma, maturity):
    """European call, no dividends, constant volatility and continuously compounded rate."""
    if not (s0 > 0 and strike > 0 and sigma >= 0 and maturity >= 0):
        raise ValueError("invalid Black-Scholes inputs")
    if maturity == 0:
        return max(s0 - strike, 0.0)
    if sigma == 0:
        return max(s0 - strike*exp(-rate*maturity), 0.0)
    vol = sigma*sqrt(maturity)
    d1 = (log(s0/strike)+(rate+0.5*sigma*sigma)*maturity)/vol
    d2 = d1-vol
    nd = NormalDist()
    return s0*nd.cdf(d1)-strike*exp(-rate*maturity)*nd.cdf(d2)


def mc_call(s0, strike, rate, sigma, maturity, paths=10000, seed=0):
    """Risk-neutral MC with unbiased sample variance standard error."""
    if paths < 2:
        raise ValueError("at least two paths required for standard error")
    samples = gbm_exact_terminal(s0,rate,sigma,maturity,paths,seed)
    payoff = [exp(-rate*maturity)*max(s-strike,0) for s in samples]
    m = mean(payoff)
    se = sqrt(sum((v-m)**2 for v in payoff)/(paths*(paths-1)))
    return {"price":m,"standard_error":se,"paths":paths}
