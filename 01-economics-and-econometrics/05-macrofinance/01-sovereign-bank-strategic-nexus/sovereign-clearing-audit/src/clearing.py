"""Anchored static Eisenberg--Noe clearing and sovereign asset stress.

Two-sided numerical brackets, NOT directed-rounding interval arithmetic.
Monetary values are synthetic; gross unpaid obligations are not social losses.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
import math
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linprog

Vector = NDArray[np.float64]


@dataclass(frozen=True)
class Network:
    liabilities: Vector  # L[i,j]: i owes j
    outside: Vector

    def __post_init__(self) -> None:
        debt, o = np.array(self.liabilities, dtype=float, copy=True), np.array(self.outside, dtype=float, copy=True)
        n = len(o) if o.ndim == 1 else 0
        if not n or debt.shape != (n, n) or not np.isfinite(debt).all() or not np.isfinite(o).all():
            raise ValueError('Finite square liabilities and matching nonempty outside vector required')
        if (debt < 0).any() or (o < 0).any() or np.any(np.diag(debt) != 0):
            raise ValueError('Nonnegative liabilities, zero diagonal required')
        totals = debt.sum(axis=1)+o
        if not np.isfinite(totals).all() or np.any((totals > 0) & (o <= 0)):
            raise ValueError('Each debtor must owe a strictly positive amount outside')
        debt.setflags(write=False)
        o.setflags(write=False)
        object.__setattr__(self, 'liabilities', debt)
        object.__setattr__(self, 'outside', o)
        if self.beta >= 1:
            raise ValueError('Outside anchor is lost at floating-point precision')

    @property
    def total(self) -> Vector:
        return self.liabilities.sum(axis=1)+self.outside

    @property
    def pi(self) -> Vector:
        p = self.total
        return np.divide(self.liabilities, p[:, None], out=np.zeros_like(self.liabilities), where=p[:, None] > 0)

    @property
    def beta(self) -> float:
        return float(self.pi.sum(axis=1).max())


def vector(net: Network, value: Vector) -> Vector:
    x = np.asarray(value, dtype=float)
    if x.shape != net.outside.shape or not np.isfinite(x).all() or (x < 0).any():
        raise ValueError('Finite nonnegative bank vector required')
    return x


def assets(net: Network, cash: Vector, sovereign: Vector, haircut: float) -> Vector:
    if not math.isfinite(haircut) or not 0 <= haircut <= 1:
        raise ValueError('Haircut must be in [0,1]')
    result = vector(net, cash)+(1-haircut)*vector(net, sovereign)
    return vector(net, result)


def step(net: Network, x: Vector, p: Vector) -> Vector:
    return np.minimum(net.total, vector(net, x)+net.pi.T@vector(net, p))


@dataclass(frozen=True)
class Result:
    payments: Vector
    lower: Vector
    upper: Vector
    iterations: int
    width_l1: float
    residual_l1: float


def bracket(net: Network, x: Vector, tolerance: float = 1e-8, max_iterations: int = 10000) -> Result:
    """Stop on L1 upper-minus-lower width, not successive-step residual alone.

    Exact arithmetic gives lower <= p* <= upper and width bounds L1 error.
    Floating implementation is empirically checked against LP/Fraction oracles;
    this is not an outward-rounded formal interval certificate.
    """
    x = vector(net, x)
    if not math.isfinite(tolerance) or tolerance <= 0 or max_iterations < 1:
        raise ValueError('Positive finite tolerance and iteration budget required')
    lo, hi = np.zeros_like(x), net.total.copy()
    for k in range(1, max_iterations+1):
        lo, hi = step(net, x, lo), step(net, x, hi)
        width = float(np.abs(hi-lo).sum())
        if width <= tolerance:
            p = (lo+hi)/2
            return Result(p, lo, hi, k, width, float(np.abs(step(net, x, p)-p).sum()))
    raise RuntimeError(f'Payment bracket did not close: width={width:.17g}, iterations={max_iterations}')


def residual_only(net: Network, x: Vector, tolerance: float = 1e-8, max_iterations: int = 10000) -> Result:
    """Ablation mirroring the notebook's single-start successive-difference stop."""
    if not math.isfinite(tolerance) or tolerance <= 0 or max_iterations < 1:
        raise ValueError('Invalid stopping controls')
    p = net.total.copy()
    for k in range(1, max_iterations+1):
        nxt = step(net, x, p)
        difference = float(np.max(abs(nxt-p)))
        p = nxt
        if difference <= tolerance:
            return Result(p, p.copy(), p.copy(), k, float('nan'), float(np.abs(step(net, x, p)-p).sum()))
    raise RuntimeError('Residual-only iteration budget exhausted')


def lp_clear(net: Network, x: Vector) -> Vector:
    """Maximize sum payments subject to limited liability and nominal caps."""
    x = vector(net, x)
    n = len(x)
    res = linprog(-np.ones(n), A_ub=np.eye(n)-net.pi.T, b_ub=x,
                  bounds=[(0., float(v)) for v in net.total], method='highs')
    if not res.success or res.x is None:
        raise RuntimeError(f'Clearing LP failed: {res.message}')
    return np.asarray(res.x, dtype=float)


def accounting(net: Network, x: Vector, p: Vector) -> dict[str, float]:
    x, p = vector(net, x), vector(net, p)
    if np.any(p > net.total+1e-10):
        raise ValueError('Payments exceed liabilities')
    share = np.divide(net.outside, net.total, out=np.zeros_like(x), where=net.total > 0)
    outside_payment = float(share@p)
    equity = np.maximum(x+net.pi.T@p-p, 0)
    return dict(gross_unpaid=float((net.total-p).sum()), outside_unpaid=float(net.outside.sum()-outside_payment),
                outside_payment=outside_payment, equity=float(equity.sum()),
                resource_identity_error=float(x.sum()-outside_payment-equity.sum()))


def rational_clear(net: Network, x: Vector) -> tuple[F, ...]:
    """Independent active-default enumeration and Fraction Gauss-Jordan, n<=6."""
    x = vector(net, x)
    n = len(x)
    if n > 6:
        raise ValueError('Rational audit oracle capped at six banks')
    debt = [[F(str(v)) for v in row] for row in net.liabilities]
    o = [F(str(v)) for v in net.outside]
    total = [sum(row, F(0))+v for row, v in zip(debt, o)]
    pi = [[v/t if t else F(0) for v in row] for row, t in zip(debt, total)]
    xx = [F(str(v)) for v in x]
    for mask in product((0, 1), repeat=n):
        default = [i for i in range(n) if mask[i]]
        p = total.copy()
        augmented = [[F(i == j)-pi[j][i] for j in default]+[
            xx[i]+sum((pi[j][i]*p[j] for j in range(n) if not mask[j]), F(0))] for i in default]
        for k in range(len(default)):
            # Anchored nonnegative network makes each principal I-Pi^T nonsingular.
            pivot = augmented[k][k]
            augmented[k] = [v/pivot for v in augmented[k]]
            for r in range(len(default)):
                if r != k:
                    factor = augmented[r][k]
                    augmented[r] = [a-factor*b for a, b in zip(augmented[r], augmented[k])]
        for i, row in zip(default, augmented):
            p[i] = row[-1]
        if all(0 <= p[i] <= total[i] and p[i] == min(total[i], xx[i]+sum(
                (pi[j][i]*p[j] for j in range(n)), F(0))) for i in range(n)):
            return tuple(p)
    raise ArithmeticError('No rational clearing candidate found')
