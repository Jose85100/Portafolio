"""Small one-asset EN/price coupling, ternary regimes and rational coefficients.

Not a new economic model, interval certificate, or strategic sovereign game.
"""

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import math


@dataclass(frozen=True)
class Economy:
    liabilities: tuple[tuple[float, ...], ...]
    outside: tuple[float, ...]
    cash: tuple[float, ...]
    stock: tuple[float, ...]
    impact: float
    floor: float = 0.05
    fundamental: float = 1.0

    def __post_init__(self) -> None:
        n = len(self.outside)
        if (
            not 1 <= n <= 4
            or len(self.liabilities) != n
            or any(len(r) != n for r in self.liabilities)
            or len(self.cash) != n
            or len(self.stock) != n
        ):
            raise ValueError("Matching bank vectors/matrix, one to four banks required")
        values = (
            *self.outside,
            *self.cash,
            *self.stock,
            *(v for row in self.liabilities for v in row),
            self.impact,
            self.floor,
            self.fundamental,
        )
        if any(not math.isfinite(v) or not 0 <= v <= 100 for v in values):
            raise ValueError("Finite inputs in [0,100] required")
        if not 1e-6 <= self.floor <= self.fundamental or any(
            self.liabilities[i][i] for i in range(n)
        ):
            raise ValueError("Positive price floor and zero diagonal required")
        for row, outside in zip(self.liabilities, self.outside):
            total = sum(row) + outside
            if total and outside / total < 0.01:
                raise ValueError("Debtors need at least one percent external anchor")

    @property
    def total(self) -> tuple[float, ...]:
        return tuple(sum(row) + o for row, o in zip(self.liabilities, self.outside))

    @property
    def pi(self) -> tuple[tuple[float, ...], ...]:
        return tuple(
            tuple(v / t if t else 0.0 for v in row)
            for row, t in zip(self.liabilities, self.total)
        )


def _solve(matrix: list[list[F]], rhs: list[F]) -> list[F]:
    """Gauss-Jordan; anchored principal EN matrix is a nonsingular M-matrix."""
    rows = [row[:] + [b] for row, b in zip(matrix, rhs)]
    for k in range(len(rows)):
        pivot = rows[k][k]
        if not pivot:
            raise ArithmeticError("Unexpected singular anchored matrix")
        rows[k] = [x / pivot for x in rows[k]]
        for i in range(len(rows)):
            if i != k:
                factor = rows[i][k]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[k])]
    return [r[-1] for r in rows]


def _dec(x: F) -> Decimal:
    return Decimal(x.numerator) / Decimal(x.denominator)


@dataclass(frozen=True)
class Solution:
    price: float
    payments: tuple[float, ...]
    sales: tuple[float, ...]
    residual: float


def evaluate(
    e: Economy, price: float, payments: tuple[float, ...]
) -> tuple[tuple[float, ...], float, tuple[float, ...]]:
    n = len(e.outside)
    if (
        len(payments) != n
        or not math.isfinite(price)
        or not e.floor <= price <= e.fundamental
        or any(
            not math.isfinite(p) or p < 0 or p > t + 1e-8
            for p, t in zip(payments, e.total)
        )
    ):
        raise ValueError("Invalid price or payments")
    incoming = tuple(
        math.fsum(e.pi[j][i] * payments[j] for j in range(n)) for i in range(n)
    )
    pnew = tuple(
        min(t, c + price * s + r)
        for t, c, s, r in zip(e.total, e.cash, e.stock, incoming)
    )
    sale = tuple(
        min(s, max(t - c - r, 0.0) / price)
        for t, c, s, r in zip(e.total, e.cash, e.stock, incoming)
    )
    qnew = max(e.floor, e.fundamental - e.impact * math.fsum(sale))
    return pnew, qnew, sale


def census(e: Economy) -> tuple[Solution, ...]:
    """3^n regimes:0 default/all sold;1 solvent/sells;2 solvent/no sales.

    Rational inequalities determine each price interval. Quadratic candidates
    use Decimal80. Numerical output is audited, not interval-certified.
    """
    n = len(e.outside)
    debt = [[F(str(v)) for v in row] for row in e.liabilities]
    outside, cash, stock = (
        [F(str(v)) for v in a] for a in (e.outside, e.cash, e.stock)
    )
    total = [sum(row, F(0)) + o for row, o in zip(debt, outside)]
    pi = [[v / t if t else F(0) for v in row] for row, t in zip(debt, total)]
    impact, floor, q0 = (F(str(v)) for v in (e.impact, e.floor, e.fundamental))
    candidates: list[Solution] = []
    with localcontext() as ctx:
        ctx.prec = 80
        eps = Decimal("1e-55")
        for state in product(range(3), repeat=n):
            default = [i for i in range(n) if state[i] == 0]
            matrix = [[F(i == j) - pi[j][i] for j in default] for i in default]
            rhs = [
                cash[i]
                + sum((pi[j][i] * total[j] for j in range(n) if state[j] != 0), F(0))
                for i in default
            ]
            intercept, slope = total[:], [F(0)] * n
            for i, u, v in zip(
                default,
                _solve(matrix, rhs),
                _solve(matrix, [stock[i] for i in default]),
            ):
                intercept[i], slope[i] = u, v
            inc_u = [
                sum((pi[j][i] * intercept[j] for j in range(n)), F(0)) for i in range(n)
            ]
            inc_v = [
                sum((pi[j][i] * slope[j] for j in range(n)), F(0)) for i in range(n)
            ]
            # Each pair(u,v) encodes u+v*q >=0.
            constraints: list[tuple[F, F]] = []
            a, b = F(0), F(0)
            for i in range(n):
                if state[i] == 0:
                    constraints.extend(
                        [(intercept[i], slope[i]), (total[i] - intercept[i], -slope[i])]
                    )
                    a += stock[i]
                else:
                    gap = total[i] - cash[i] - inc_u[i]
                    constraints.append((-gap, stock[i] + inc_v[i]))
                    if state[i] == 1:
                        constraints.append((gap, -inc_v[i]))
                        a -= inc_v[i]
                        b += gap
                    else:
                        constraints.append((-gap, inc_v[i]))
            low, high = floor, q0
            valid = True
            for u, v in constraints:
                if v > 0:
                    low = max(low, -u / v)
                elif v < 0:
                    high = min(high, -u / v)
                elif u < 0:
                    valid = False
            if not valid or low > high:
                continue
            roots: list[Decimal] = []
            if low <= floor <= high and q0 - impact * (a + b / floor) <= floor:
                roots.append(_dec(floor))
            coefficient = q0 - impact * a
            discriminant = coefficient**2 - 4 * impact * b
            if discriminant >= 0:
                square = _dec(discriminant).sqrt()
                if discriminant > 0 and square < Decimal("1e-9"):
                    center = _dec(coefficient) / 2
                    if _dec(low) <= center <= _dec(high):
                        raise ArithmeticError(
                            "Quadratic roots too close for output resolution"
                        )
                roots.extend(
                    [(_dec(coefficient) - square) / 2, (_dec(coefficient) + square) / 2]
                )
            for q in roots:
                if not _dec(low) - eps <= q <= _dec(high) + eps or q <= 0:
                    continue
                price = min(e.fundamental, max(e.floor, float(q)))
                payments = tuple(
                    min(t, max(0.0, float(_dec(u) + _dec(v) * q)))
                    for t, u, v in zip(e.total, intercept, slope)
                )
                pnew, qnew, sale = evaluate(e, price, payments)
                residual = max(
                    abs(qnew - price), *(abs(p - pp) for p, pp in zip(payments, pnew))
                )
                if residual > 1e-8:
                    raise ArithmeticError("Candidate fails joint residual audit")
                candidates.append(Solution(price, payments, sale, residual))
    unique: list[Solution] = []
    for candidate in sorted(candidates, key=lambda r: r.price):
        if unique and abs(candidate.price - unique[-1].price) < 1e-12:
            if (
                max(abs(p - q) for p, q in zip(candidate.payments, unique[-1].payments))
                > 1e-8
            ):
                raise ArithmeticError("Inconsistent payments at duplicate price")
            continue
        if unique and candidate.price - unique[-1].price < 1e-9:
            raise ArithmeticError("Distinct prices below output resolution")
        unique.append(candidate)
    if not unique:
        raise ArithmeticError("No solution: numerical implementation failure")
    return tuple(unique)


def accounts(e: Economy, solution: Solution) -> dict[str, float]:
    evaluate(e, solution.price, solution.payments)
    incoming = [
        sum(e.pi[j][i] * solution.payments[j] for j in range(len(e.outside)))
        for i in range(len(e.outside))
    ]
    equities = [
        c + solution.price * s + r - p
        for c, s, r, p in zip(e.cash, e.stock, incoming, solution.payments)
    ]
    equity = sum(equities)
    external_paid = sum(
        o / t * p if t else 0.0
        for o, t, p in zip(e.outside, e.total, solution.payments)
    )
    resources = sum(e.cash) + solution.price * sum(e.stock)
    return dict(
        outside_paid=external_paid,
        outside_unpaid=sum(e.outside) - external_paid,
        gross_unpaid=sum(e.total) - sum(solution.payments),
        equity=equity,
        marked_loss=(e.fundamental - solution.price) * sum(e.stock),
        identity_error=resources - external_paid - equity,
        min_equity=min(equities),
    )
