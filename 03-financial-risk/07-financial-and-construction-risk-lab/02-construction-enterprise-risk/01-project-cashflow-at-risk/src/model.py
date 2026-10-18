"""Baseline Monte Carlo cash-flow-at-risk engine for construction projects.

All amounts are in a single currency. Synthetic assumptions only; not calibrated.
"""
from dataclasses import dataclass
from random import Random
from statistics import mean
from math import ceil, isfinite

@dataclass(frozen=True)
class Project:
    opening_cash: float
    monthly_collections: tuple[float, ...]
    monthly_costs: tuple[float, ...]
    monthly_debt_service: tuple[float, ...]
    liquidity_floor: float = 0.0

    def __post_init__(self):
        n = len(self.monthly_collections)
        if n == 0 or len(self.monthly_costs) != n or len(self.monthly_debt_service) != n:
            raise ValueError('All monthly series must have the same positive length')
        if not isfinite(self.opening_cash) or not isfinite(self.liquidity_floor) or self.opening_cash < 0:
            raise ValueError('Opening cash must be finite/nonnegative and floor finite')
        if any(not isfinite(x) or x < 0 for series in (self.monthly_collections, self.monthly_costs, self.monthly_debt_service) for x in series):
            raise ValueError('Flows must be nonnegative')


def simulate(project: Project, scenarios: int = 1000, seed: int = 42,
             collection_vol: float = 0.15, cost_vol: float = 0.12,
             common_shock_weight: float = 0.5) -> dict:
    """Simulate common adverse factor: lower collections and higher costs.

    Shocks are clipped at zero for collections/costs. Quantile uses nearest rank.
    Results report peak shortfall vs liquidity floor, not a VaR of P&L.
    """
    if (isinstance(scenarios, bool) or not isinstance(scenarios, int) or scenarios < 1
            or not all(isfinite(x) for x in (collection_vol, cost_vol, common_shock_weight))
            or collection_vol < 0 or cost_vol < 0 or not 0 <= common_shock_weight <= 1):
        raise ValueError('Invalid simulation parameters')
    rng = Random(seed)
    shortfalls = []
    terminal_cash = []
    for _ in range(scenarios):
        cash = project.opening_cash
        peak = max(0.0, project.liquidity_floor - cash)
        for revenue, cost, debt in zip(project.monthly_collections, project.monthly_costs, project.monthly_debt_service):
            macro = rng.gauss(0, 1)
            rev_shock = common_shock_weight * macro + (1-common_shock_weight**2)**0.5 * rng.gauss(0, 1)
            cost_shock = -common_shock_weight * macro + (1-common_shock_weight**2)**0.5 * rng.gauss(0, 1)
            collections = max(0.0, revenue * (1 + collection_vol * rev_shock))
            costs = max(0.0, cost * (1 + cost_vol * cost_shock))
            cash += collections - costs - debt
            if not isfinite(cash): raise ArithmeticError("Cash accumulation overflow")
            peak = max(peak, project.liquidity_floor - cash)
        shortfalls.append(peak)
        terminal_cash.append(cash)
    ordered = sorted(shortfalls)
    q95 = ordered[ceil(0.95 * scenarios) - 1]
    return {'scenarios': scenarios, 'probability_shortfall': sum(s > 0 for s in shortfalls) / scenarios,
            'expected_peak_shortfall': mean(shortfalls), 'peak_shortfall_q95': q95,
            'mean_terminal_cash': mean(terminal_cash)}
