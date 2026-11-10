"""Numerical research baselines. No regulatory parameter tables or compliance claim."""
import math
import random

def _finite(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError("Expected finite number")
    return x

def _positive(x):
    x = _finite(x)
    if x < 0:
        raise ValueError("Expected nonnegative number")
    return x

def _prob(x):
    x = _positive(x)
    if x > 1:
        raise ValueError("Probability outside [0,1]")
    return x

def weighted_rwa(exposures, weights):
    """Illustrative credit-only weighted sum; weights supplied by caller."""
    exposures, weights = list(exposures), list(weights)
    if not exposures or len(exposures) != len(weights):
        raise ValueError("Nonempty aligned inputs required")
    return math.fsum(_positive(e) * _positive(w) for e, w in zip(exposures, weights))

def ecl(hazards, lgds, eads, rate=0.0):
    """One scenario; conditional hazards, equal annual periods, future defaults only."""
    hazards, lgds, eads = list(hazards), list(lgds), list(eads)
    if not hazards or len(hazards) != len(lgds) or len(hazards) != len(eads):
        raise ValueError("Nonempty aligned annual term structures required")
    rate = _finite(rate)
    if rate <= -1:
        raise ValueError("Discount rate must exceed -1")
    survival, terms = 1.0, []
    for t, (h, l, e) in enumerate(zip(hazards, lgds, eads), 1):
        h, l, e = _prob(h), _prob(l), _positive(e)
        terms.append(survival * h * l * e / (1 + rate) ** t)
        survival *= 1 - h
    return math.fsum(terms)

def empirical_es(losses, alpha=0.975):
    """Exact upper-tail integral for equally weighted empirical observations."""
    losses = sorted((_finite(x) for x in losses), reverse=True)
    alpha = _prob(alpha)
    if not losses or alpha == 1:
        raise ValueError("Nonempty observations and alpha < 1 required")
    mass = len(losses) * (1 - alpha)
    whole = math.floor(mass)
    fraction = mass - whole
    total = math.fsum(losses[:whole])
    if fraction:
        total += fraction * losses[whole]
    return total / mass

def cash_path(initial, net_flows):
    """Include opening cash; signed flows, no behavioral assumptions."""
    balances = [_positive(initial)]
    for flow in net_flows:
        balances.append(balances[-1] + _finite(flow))
    return balances

def operational_losses(annual_frequency, mean_severity, years=1000, seed=0):
    """Compound Poisson/exponential baseline; not a regulatory capital model."""
    frequency, severity = _positive(annual_frequency), _positive(mean_severity)
    if isinstance(years, bool) or not isinstance(years, int) or years < 1:
        raise ValueError("Positive integer years required")
    rng = random.Random(seed)
    results = []
    for _ in range(years):
        elapsed, total = 0.0, 0.0
        if frequency and severity:
            while True:
                elapsed += rng.expovariate(frequency)
                if elapsed > 1:
                    break
                total += rng.expovariate(1 / severity)
        results.append(total)
    return results

def kri_status(value, warning, breach, higher_is_worse=True):
    """Missing value is unknown; thresholds are policy inputs, not legal limits."""
    warning, breach = _finite(warning), _finite(breach)
    if not isinstance(higher_is_worse, bool):
        raise ValueError("Direction must be bool")
    if (higher_is_worse and warning > breach) or (not higher_is_worse and warning < breach):
        raise ValueError("Threshold order conflicts with risk direction")
    if value is None:
        return "unknown"
    value = _finite(value)
    if higher_is_worse:
        return "breach" if value >= breach else "warning" if value >= warning else "normal"
    return "breach" if value <= breach else "warning" if value <= warning else "normal"
