"""One-asset minimal liquidation: enumerate price roots by rational regimes.

No interbank payments, optimization or sovereign default in this component.
Decimal arithmetic is high precision, not directed-rounding certification.
"""

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction as F
import math


@dataclass(frozen=True)
class Market:
    """Cash/debt in numeraire, holdings in units; impact in price per unit."""

    cash: tuple[float, ...]
    debt: tuple[float, ...]
    holdings: tuple[float, ...]
    impact: float
    fundamental: float = 1.0
    floor: float = 0.05

    def __post_init__(self) -> None:
        if (
            not self.cash
            or len(self.cash) != len(self.debt)
            or len(self.cash) != len(self.holdings)
        ):
            raise ValueError("Nonempty matching bank vectors required")
        values = (
            *self.cash,
            *self.debt,
            *self.holdings,
            self.impact,
            self.fundamental,
            self.floor,
        )
        if any(not math.isfinite(x) or x < 0 or x > 1e6 for x in values):
            raise ValueError("Finite inputs in [0,1e6] required")
        if not 1e-8 <= self.floor <= self.fundamental:
            raise ValueError("Require 1e-8 <= floor <= fundamental")

    @property
    def gaps(self) -> tuple[float, ...]:
        return tuple(max(d - c, 0.0) for c, d in zip(self.cash, self.debt))


def sales(m: Market, price: float) -> tuple[float, ...]:
    """Price-taking rule, not a strategic optimal liquidation policy."""
    if not math.isfinite(price) or not m.floor <= price <= m.fundamental:
        raise ValueError("Price outside supported market interval")
    return tuple(min(s, d / price) for s, d in zip(m.holdings, m.gaps))


def update(m: Market, price: float) -> float:
    return max(m.floor, m.fundamental - m.impact * sum(sales(m, price)))


@dataclass(frozen=True)
class Root:
    price: float
    residual: float
    slope_left: float
    slope_right: float
    stability: str


def _decimal(x: F) -> Decimal:
    return Decimal(x.numerator) / Decimal(x.denominator)


def equilibria(m: Market) -> tuple[Root, ...]:
    """Enumerate floor and quadratic roots on every liquidation regime.

    Coefficients/discriminant signs are rational for decimal-string inputs.
    Distinct roots closer than 1e-10 fail closed; outputs are float64 prices.
    O(n^2) rational work, intentionally a small-market research prototype.
    """
    cash, debt, stock = ([F(str(v)) for v in a] for a in (m.cash, m.debt, m.holdings))
    gaps = [max(d - c, F(0)) for c, d in zip(cash, debt)]
    a, q0, floor = (F(str(v)) for v in (m.impact, m.fundamental, m.floor))
    cuts = sorted(
        {floor, q0, *(d / s for d, s in zip(gaps, stock) if s and floor < d / s < q0)}
    )
    with localcontext() as ctx:
        ctx.prec = 64
        eps = Decimal("1e-48")
        candidates: list[Decimal] = []
        floor_supply = sum((min(s, d / floor) for s, d in zip(stock, gaps)), F(0))
        if q0 - a * floor_supply <= floor:
            candidates.append(_decimal(floor))
        for left, right in zip(cuts, cuts[1:]):
            mid = (left + right) / 2
            saturated = sum((s for s, d in zip(stock, gaps) if d >= s * mid), F(0))
            unmet = sum((d for s, d in zip(stock, gaps) if d < s * mid), F(0))
            b, c = q0 - a * saturated, a * unmet
            disc = b * b - 4 * c
            if disc < 0:
                continue
            square = _decimal(disc).sqrt()
            # Positive exact discriminant must not be rounded into a double root.
            if disc > 0 and square < Decimal("1e-10"):
                low, high = (_decimal(b) - square) / 2, (_decimal(b) + square) / 2
                if _decimal(left) - eps <= low and high <= _decimal(right) + eps:
                    raise ArithmeticError(
                        "Distinct quadratic roots below output resolution"
                    )
            for root in ((_decimal(b) - square) / 2, (_decimal(b) + square) / 2):
                if _decimal(left) - eps <= root <= _decimal(right) + eps and root > 0:
                    candidates.append(root)
        # The degenerate domain floor=q0 contains exactly one price.
        if floor == q0:
            candidates.append(_decimal(floor))
        unique: list[Decimal] = []
        for root in sorted(candidates):
            if unique and abs(root - unique[-1]) < eps:
                continue
            if unique and root - unique[-1] < Decimal("1e-10"):
                raise ArithmeticError("Distinct roots too close for output resolution")
            unique.append(root)
    result = []
    for value in unique:
        q = min(m.fundamental, max(m.floor, float(value)))
        # One-sided derivatives, including liquidation and price-floor kinks.
        left_sum = sum(float(d) for s, d in zip(stock, gaps) if d < s * F(str(q)))
        right_sum = sum(float(d) for s, d in zip(stock, gaps) if d <= s * F(str(q)))
        left_slope = m.impact * left_sum / q**2
        right_slope = m.impact * right_sum / q**2
        if q == m.floor:
            left_slope = 0.0
            if m.fundamental - m.impact * sum(sales(m, q)) < q - 1e-12:
                right_slope = 0.0
        lo, hi = min(left_slope, right_slope), max(left_slope, right_slope)
        stability = (
            "stable"
            if hi < 1 - 1e-9
            else "unstable"
            if lo > 1 + 1e-9
            else "marginal/kink"
        )
        residual = abs(update(m, q) - q)
        if residual > 1e-10:
            raise ArithmeticError("Price residual exceeds supported tolerance")
        result.append(Root(q, residual, left_slope, right_slope, stability))
    if not result:
        raise ArithmeticError("No root found: numerical implementation failure")
    return tuple(result)


def iterate(
    m: Market, start: float, tolerance: float = 1e-12, budget: int = 10000
) -> tuple[float, int]:
    """Single-start baseline; residual stopping is not root enumeration."""
    if not math.isfinite(tolerance) or tolerance <= 0 or budget < 1:
        raise ValueError("Positive finite tolerance and iteration budget required")
    sales(m, start)
    q = start
    for count in range(1, budget + 1):
        new = update(m, q)
        if abs(new - q) <= tolerance:
            return new, count
        q = new
    raise RuntimeError("Iteration budget exhausted")


def balance(m: Market, price: float) -> dict[str, float]:
    """Bank-sector accounting; lost marked value is not welfare destruction."""
    quantities = sales(m, price)
    paid = [min(d, c + price * g) for c, d, g in zip(m.cash, m.debt, quantities)]
    remaining_cash = sum(c + price * g - p for c, g, p in zip(m.cash, quantities, paid))
    remaining_stock = sum(s - g for s, g in zip(m.holdings, quantities))
    assets = sum(m.cash) + price * sum(m.holdings)
    equity = remaining_cash + price * remaining_stock
    return dict(
        price=price,
        sales=sum(quantities),
        paid=sum(paid),
        unpaid=sum(m.debt) - sum(paid),
        equity=equity,
        marked_loss=(m.fundamental - price) * sum(m.holdings),
        identity_error=assets - sum(paid) - equity,
    )
