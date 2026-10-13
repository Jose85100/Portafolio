"""Construction quantitative risk baselines; deterministic, dependency-free, not calibrated."""
from math import ceil, exp, log, sqrt
from random import Random
from statistics import mean


def empirical_var_es(losses, alpha=0.95):
    if not losses or not 0 < alpha < 1:
        raise ValueError("Nonempty losses and 0 < alpha < 1 required")
    ordered = sorted(float(x) for x in losses)
    k = ceil(alpha * len(ordered)) - 1
    return {"var": ordered[k], "es": mean(ordered[k:])}


def project_finance(cash_available, debt_service, debt_outstanding, discount_rate=0.1):
    if len(cash_available) != len(debt_service) or not cash_available or debt_outstanding < 0 or discount_rate <= -1:
        raise ValueError("Invalid project finance inputs")
    if any(x < 0 for x in debt_service):
        raise ValueError("Debt service cannot be negative")
    dscr = [cf / ds if ds > 0 else None for cf, ds in zip(cash_available, debt_service)]
    pv_cfads = sum(cf / (1 + discount_rate) ** (t + 1) for t, cf in enumerate(cash_available))
    return {"dscr": dscr, "llcr": pv_cfads / debt_outstanding if debt_outstanding else None,
            "minimum_dscr": min((x for x in dscr if x is not None), default=None)}


def critical_path(durations, dependencies):
    """Longest path in DAG, node durations. Dependencies map task -> prerequisites."""
    if not durations or any(v < 0 for v in durations.values()):
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
        state[task] = 2
        return finish[task]
    return {"project_duration": max(visit(task) for task in durations), "earliest_finish": finish}


def schedule_monte_carlo(triangular_tasks, dependencies, n=1000, seed=42):
    """PERT-like triangular draws (min, mode, max), no dependency calibration."""
    if n < 1 or not triangular_tasks:
        raise ValueError("Invalid scenario count/tasks")
    for low, mode, high in triangular_tasks.values():
        if not 0 <= low <= mode <= high:
            raise ValueError("Require 0 <= min <= mode <= max")
    rng = Random(seed)
    durations = [critical_path({k: rng.triangular(low, high, mode) for k, (low, mode, high) in triangular_tasks.items()}, dependencies)["project_duration"] for _ in range(n)]
    return {"mean_duration": mean(durations), "p95_duration": empirical_var_es(durations)["var"]}


def correlated_project_losses(exposures, pds, lgds, scenarios=2000, seed=42, rho=0.25):
    """One-factor Gaussian threshold model; constant pairwise latent correlation rho."""
    if not exposures or not len(exposures) == len(pds) == len(lgds) or scenarios < 1 or not 0 <= rho <= 1:
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
