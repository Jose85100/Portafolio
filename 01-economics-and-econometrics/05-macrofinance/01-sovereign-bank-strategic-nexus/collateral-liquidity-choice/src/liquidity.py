"""One-bank collateral/liquidation choice under a reduced-form price impact."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Problem:
    shortfall: float
    holdings: float
    fundamental: float
    impact: float
    floor: float
    pledgeable: float
    borrowing_rate: float

    def __post_init__(self) -> None:
        values = (
            self.shortfall,
            self.holdings,
            self.fundamental,
            self.impact,
            self.floor,
            self.pledgeable,
            self.borrowing_rate,
        )
        if any(not math.isfinite(value) for value in values):
            raise ValueError("Finite inputs required")
        if (
            self.shortfall < 0
            or self.holdings <= 0
            or self.fundamental <= 0
            or self.impact < 0
            or not 0 < self.floor <= self.fundamental
            or not 0 <= self.pledgeable <= 1
            or self.borrowing_rate < 0
        ):
            raise ValueError("Invalid nonnegative balance-sheet parameters")


@dataclass(frozen=True)
class Choice:
    liquidation: float
    borrowing: float
    price: float
    cost: float
    collateral_slack: float
    liquidity_slack: float


def _quadratic_roots(a: float, b: float, c: float) -> tuple[float, ...]:
    tolerance = 1e-14
    if abs(a) <= tolerance:
        return () if abs(b) <= tolerance else (-c / b,)
    discriminant = b * b - 4 * a * c
    if discriminant < -tolerance:
        return ()
    discriminant = max(0.0, discriminant)
    root = math.sqrt(discriminant)
    return ((-b - root) / (2 * a), (-b + root) / (2 * a))


def evaluate(problem: Problem, liquidation: float) -> Choice:
    if not math.isfinite(liquidation) or not 0 <= liquidation <= problem.holdings:
        raise ValueError("Liquidation must lie within holdings")
    price = max(problem.floor, problem.fundamental - problem.impact * liquidation)
    sale_cash = price * liquidation
    borrowing = max(0.0, problem.shortfall - sale_cash)
    collateral_capacity = problem.pledgeable * price * (problem.holdings - liquidation)
    collateral_slack = collateral_capacity - borrowing
    liquidity_slack = sale_cash + borrowing - problem.shortfall
    fire_sale_loss = (problem.fundamental - price) * liquidation
    cost = fire_sale_loss + problem.borrowing_rate * borrowing
    return Choice(
        liquidation,
        borrowing,
        price,
        cost,
        collateral_slack,
        liquidity_slack,
    )


def _candidate_points(problem: Problem) -> tuple[float, ...]:
    """All boundaries and stationary points of the piecewise quadratic problem."""
    g, s, q0, a, floor, theta, rate = (
        problem.shortfall,
        problem.holdings,
        problem.fundamental,
        problem.impact,
        problem.floor,
        problem.pledgeable,
        problem.borrowing_rate,
    )
    candidates = [0.0, s]
    if a > 0:
        candidates.append((q0 - floor) / a)
        candidates.append(rate * q0 / (2 * a * (1 + rate)))
    candidates.extend(_quadratic_roots(a, -q0, g))
    # Borrowing requirement equals collateral capacity before the price floor.
    candidates.extend(
        _quadratic_roots(
            a * (1 - theta),
            -q0 + theta * q0 + theta * a * s,
            g - theta * q0 * s,
        )
    )
    # Same equality in the floor-price region.
    floor_denominator = floor * (theta - 1)
    if abs(floor_denominator) > 1e-14:
        candidates.append(-(g - theta * floor * s) / floor_denominator)
    return tuple(sorted({min(s, max(0.0, x)) for x in candidates if math.isfinite(x)}))


def solve(problem: Problem) -> Choice:
    feasible = [
        choice
        for choice in (evaluate(problem, x) for x in _candidate_points(problem))
        if choice.collateral_slack >= -1e-10 and choice.liquidity_slack >= -1e-10
    ]
    if not feasible:
        raise ArithmeticError(
            "Shortfall cannot be funded by sale and collateralized loan"
        )
    return min(feasible, key=lambda choice: (choice.cost, choice.liquidation))


def liquidation_only(problem: Problem) -> Choice:
    feasible = [
        choice
        for choice in (evaluate(problem, x) for x in _candidate_points(problem))
        if choice.borrowing <= 1e-10
    ]
    if not feasible:
        raise ArithmeticError("Pure liquidation cannot cover the shortfall")
    return min(feasible, key=lambda choice: (choice.cost, choice.liquidation))


def dense_grid(problem: Problem, points: int = 100_001) -> Choice:
    if points < 2:
        raise ValueError("At least two grid points required")
    best: Choice | None = None
    for index in range(points):
        choice = evaluate(problem, problem.holdings * index / (points - 1))
        if choice.collateral_slack >= -1e-12 and (
            best is None or choice.cost < best.cost
        ):
            best = choice
    if best is None:
        raise ArithmeticError("Grid found no feasible choice")
    return best
