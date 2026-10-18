"""Construction quantitative risk baselines; deterministic, dependency-free, not calibrated."""
from math import ceil, exp, log, sqrt, isfinite, fsum
from random import Random
from statistics import mean


def _finite_values(values, name):
    values = tuple(float(x) for x in values)
    if not values or not all(isfinite(x) for x in values):
        raise ValueError(f"{name} must contain finite values")
    return values


def _count(value, name, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def empirical_var_es(losses, alpha=0.95):
    """Nearest-rank VaR; ES integrates exactly 1-alpha probability mass.

    The boundary atom is included fractionally. This replaces the old average
    of all ranks from VaR onward, which was not the same discrete risk measure.
    Input values are binary64; this baseline is not an underflow-safe oracle.
    """
    ordered = sorted(_finite_values(losses, "losses"))
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("0 < alpha < 1 required")
    n = len(ordered)
    k = max(0, min(n - 1, ceil(alpha * n) - 1))
    mass = n * (1 - alpha)
    whole = int(mass)
    fractional = mass - whole
    # Divide each coefficient before multiplication, limiting overflow in a
    # representable tail mean; fsum accumulates mixed-sign contributions.
    contributions = [x / mass for x in ordered[n-whole:]] if whole else []
    if fractional:
        contributions.append(ordered[n-whole-1] * (fractional / mass))
    try:
        es = fsum(contributions)
    except OverflowError as error:
        raise ArithmeticError("ES accumulation overflow") from error
    if not isfinite(es):
        raise ArithmeticError("ES is not finite")
    return {"var": ordered[k], "es": es}


def project_finance(cash_available, debt_service, debt_outstanding, discount_rate=0.1):
    """CFADS and debt service use one currency and equally spaced periods.

    Zero debt service yields no DSCR (None), not infinity or zero. Negative
    CFADS is permitted to represent a cash deficit; debt service is nonnegative.
    """
    cash_available = _finite_values(cash_available, "cash_available")
    debt_service = _finite_values(debt_service, "debt_service")
    if (len(cash_available) != len(debt_service)
            or not isfinite(debt_outstanding) or debt_outstanding < 0
            or not isfinite(discount_rate) or discount_rate <= -1
            or any(x < 0 for x in debt_service)):
        raise ValueError("Invalid project finance inputs")
    dscr = [cf / ds if ds > 0 else None for cf, ds in zip(cash_available, debt_service)]
    try:
        pv_cfads = fsum(cf / (1 + discount_rate) ** (t + 1) for t, cf in enumerate(cash_available))
        llcr = pv_cfads / debt_outstanding if debt_outstanding else None
    except (OverflowError, ZeroDivisionError) as error:
        raise ArithmeticError("Discounting outside the numeric domain") from error
    if not isfinite(pv_cfads) or (llcr is not None and not isfinite(llcr)) or any(x is not None and not isfinite(x) for x in dscr):
        raise ArithmeticError("Nonfinite finance result")
    return {"dscr": dscr, "llcr": llcr,
            "minimum_dscr": min((x for x in dscr if x is not None), default=None)}


def critical_path(durations, dependencies):
    """Longest path in DAG, node durations. Dependencies map task -> prerequisites."""
    if not durations or any(not isfinite(v) or v < 0 for v in durations.values()):
        raise ValueError("Nonempty tasks with nonnegative durations required")
    if set(dependencies) - set(durations) or any(set(p) - set(durations) for p in dependencies.values()):
        raise ValueError("Unknown task")
    state, finish = {}, {}
    def visit(task):
        if state.get(task) == 1:
            raise ValueError("Cycle in schedule")
        if state.get(task) == 2:
            return finish[task]
        state[task] = 1
        finish[task] = durations[task] + max((visit(p) for p in dependencies.get(task, ())), default=0)
        if not isfinite(finish[task]): raise ArithmeticError("Schedule accumulation overflow")
        state[task] = 2
        return finish[task]
    return {"project_duration": max(visit(task) for task in durations), "earliest_finish": finish}


def schedule_monte_carlo(triangular_tasks, dependencies, n=1000, seed=42):
    """PERT-like triangular draws (min, mode, max), no dependency calibration."""
    _count(n, "n")
    if not triangular_tasks:
        raise ValueError("Invalid scenario count/tasks")
    for low, mode, high in triangular_tasks.values():
        if not all(isfinite(x) for x in (low, mode, high)) or not 0 <= low <= mode <= high:
            raise ValueError("Require 0 <= min <= mode <= max")
    rng = Random(seed)
    durations = [critical_path({k: rng.triangular(low, high, mode) for k, (low, mode, high) in triangular_tasks.items()}, dependencies)["project_duration"] for _ in range(n)]
    return {"mean_duration": mean(durations), "p95_duration": empirical_var_es(durations)["var"]}


def correlated_project_losses(exposures, pds, lgds, scenarios=2000, seed=42, rho=0.25):
    """One-factor Gaussian threshold model; constant pairwise latent correlation rho."""
    exposures = _finite_values(exposures, "exposures")
    pds = _finite_values(pds, "pds")
    lgds = _finite_values(lgds, "lgds")
    _count(scenarios, "scenarios")
    if not len(exposures) == len(pds) == len(lgds) or not isfinite(rho) or not 0 <= rho <= 1:
        raise ValueError("Invalid portfolio inputs")
    if any(e < 0 or not 0 <= p <= 1 or not 0 <= l <= 1 for e, p, l in zip(exposures, pds, lgds)):
        raise ValueError("Invalid EAD/PD/LGD")
    # Inverse Gaussian CDF via stdlib NormalDist.
    from statistics import NormalDist
    nd = NormalDist()
    thresholds = [nd.inv_cdf(p) if 0 < p < 1 else (-float("inf") if p == 0 else float("inf")) for p in pds]
    rng = Random(seed)
    losses = []
    for _ in range(scenarios):
        z = rng.gauss(0, 1)
        losses.append(sum(e * l for e, l, threshold in zip(exposures, lgds, thresholds)
                          if sqrt(rho) * z + sqrt(1 - rho) * rng.gauss(0, 1) < threshold))
    tail = empirical_var_es(losses)
    return {"expected_loss": mean(losses), "var95": tail["var"], "es95": tail["es"], "scenarios": scenarios}
