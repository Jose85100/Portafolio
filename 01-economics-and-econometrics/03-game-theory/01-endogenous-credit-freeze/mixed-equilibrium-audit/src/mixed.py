"""Isolated behavioral BNE for the existing two-lender Bayesian game.

Fail closed when a feasible singular support prevents a finite-list certificate.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linprog

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "bayesian-freeze-audit/src"))
from game import Game, equilibria, posterior  # noqa: E402

Vector = NDArray[np.float64]


class DegenerateGameError(ValueError):
    """Finite isolated-equilibrium output cannot certify this support."""


def affine(g: Game) -> tuple[Vector, NDArray[np.float64]]:
    intercept = np.zeros(4)
    matrix = np.zeros((4, 4))
    for i, s in product((0, 1), repeat=2):
        post = posterior(g, s)
        k = 2*i+s
        intercept[k] = post-g.cost
        matrix[k, 2*(1-i)] = g.complementarity*(post*(1-g.accuracy)+(1-post)*g.accuracy)
        matrix[k, 2*(1-i)+1] = g.complementarity*(post*g.accuracy+(1-post)*(1-g.accuracy))
    return intercept, matrix


def mixed_regret(g: Game, probabilities: Vector) -> float:
    x = np.asarray(probabilities, dtype=float)
    if x.shape != (4,) or not np.isfinite(x).all() or np.any(x < 0) or np.any(x > 1):
        raise ValueError("Four finite probabilities in [0,1] required")
    b, a = affine(g)
    d = b+a@x
    return float(np.max(np.maximum(d, 0)-x*d))


def solve(g: Game, tolerance: float = 1e-10) -> list[Vector]:
    """Visit all 3^4 patterns: withdraw, lend, or mix at each information type.

    Nondegenerate accepted candidates are checked by interim regret. Feasible
    singular supports abort rather than silently returning an incomplete list.
    """
    if not np.isfinite(tolerance) or not 0 < tolerance < 1e-3:
        raise ValueError("Tolerance must lie in (0,1e-3)")
    b, a = affine(g)
    points: list[Vector] = []
    for pattern in product((0, 1, 2), repeat=4):
        free = [k for k in range(4) if pattern[k] == 2]
        fixed = [k for k in range(4) if pattern[k] != 2]
        x = np.array([float(v) if v != 2 else 0. for v in pattern])
        if free:
            sub = a[np.ix_(free, free)]
            rhs = -b[free]-a[np.ix_(free, fixed)]@x[fixed]
            rank = int(np.linalg.matrix_rank(sub, tol=tolerance))
            augmented_rank = int(np.linalg.matrix_rank(np.column_stack((sub, rhs)), tol=tolerance))
            if augmented_rank > rank:
                continue
            if rank < len(free):
                # Consistency alone is not feasibility (Gambit warns about this).
                signs = np.array([1. if pattern[k] == 0 else -1. for k in fixed])
                lp: Any = linprog(np.zeros(len(free)),
                    A_ub=signs[:, None]*a[np.ix_(fixed, free)] if fixed else None,
                    b_ub=-signs*(b[fixed]+a[np.ix_(fixed, fixed)]@x[fixed]) if fixed else None,
                    A_eq=sub, b_eq=rhs, bounds=[(0., 1.)]*len(free), method="highs")
                if lp.status == 2:
                    continue
                if not lp.success:
                    raise RuntimeError(f"Singular-support LP failed: {lp.message}")
                x[free] = lp.x
                if mixed_regret(g, np.clip(x, 0, 1)) > tolerance:
                    raise RuntimeError("LP witness fails regret certification")
                raise DegenerateGameError(f"Feasible singular support {pattern}; no finite-list certificate")
            x[free] = np.linalg.solve(sub, rhs)
        if np.any(x < -tolerance) or np.any(x > 1+tolerance):
            continue
        x = np.clip(x, 0, 1)
        # Small regret alone can accept near-pure mixtures; support inequalities
        # and indifference are checked directly as well.
        d = b+a@x
        if any((pattern[k] == 0 and d[k] > tolerance) or
               (pattern[k] == 1 and d[k] < -tolerance) or
               (pattern[k] == 2 and abs(d[k]) > tolerance) for k in range(4)):
            continue
        if mixed_regret(g, x) > tolerance:
            raise RuntimeError("Candidate fails regret certification")
        if not any(np.max(np.abs(x-y)) <= tolerance for y in points):
            points.append(x)
    return sorted(points, key=lambda x: tuple(x))


def rational_oracle(g: Game) -> list[tuple[Fraction, ...]]:
    """Independent direct-state payoff sums and exact Gauss-Jordan elimination.

    Returns isolated candidates. Consistent singular supports are skipped, so
    this oracle is compared only for games certified nonsingular by solve().
    """
    pi, q, c, alpha = map(lambda v: Fraction(str(v)),
                         (g.prior, g.accuracy, g.cost, g.complementarity))
    matrix = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    b = [Fraction(0) for _ in range(4)]
    for i, s in product((0, 1), repeat=2):
        mass = sum((pi if t else 1-pi)*(q if s == t else 1-q) for t in (0, 1))
        for theta, other_signal in product((0, 1), repeat=2):
            prob = (pi if theta else 1-pi)*(q if s == theta else 1-q)*(q if other_signal == theta else 1-q)/mass
            b[2*i+s] += prob*(theta-c)
            matrix[2*i+s][2*(1-i)+other_signal] += prob*alpha
    points: set[tuple[Fraction, ...]] = set()
    for pattern in product((0, 1, 2), repeat=4):
        free = [k for k in range(4) if pattern[k] == 2]
        fixed = [k for k in range(4) if pattern[k] != 2]
        x = [Fraction(v) if v != 2 else Fraction(0) for v in pattern]
        rows = [[matrix[k][j] for j in free]+[-b[k]-sum(matrix[k][j]*x[j] for j in fixed)] for k in free]
        singular = False
        for col in range(len(free)):
            pivot = next((r for r in range(col, len(free)) if rows[r][col]), None)
            if pivot is None:
                singular = True
                break
            rows[col], rows[pivot] = rows[pivot], rows[col]
            scale = rows[col][col]
            rows[col] = [v/scale for v in rows[col]]
            for r in range(len(free)):
                if r != col:
                    weight = rows[r][col]
                    rows[r] = [v-weight*w for v, w in zip(rows[r], rows[col])]
        if singular:
            continue
        for k, row in zip(free, rows):
            x[k] = row[-1]
        if any(v < 0 or v > 1 for v in x):
            continue
        d = [b[k]+sum(matrix[k][j]*x[j] for j in range(4)) for k in range(4)]
        if all((v == 0 and gain <= 0) or (v == 1 and gain >= 0) or
               (0 < v < 1 and gain == 0) for v, gain in zip(x, d)):
            points.add(tuple(x))
    return sorted(points)


def outcomes(g: Game, x: Vector) -> dict[str, float]:
    mixed_regret(g, x)  # validate input
    lending = payoff = freeze = 0.
    for theta, s0, s1 in product((0, 1), repeat=3):
        conditional = (g.accuracy if s0 == theta else 1-g.accuracy)*(g.accuracy if s1 == theta else 1-g.accuracy)
        mass = (g.prior if theta else 1-g.prior)*conditional
        p0, p1 = x[s0], x[2+s1]
        lending += mass*(p0+p1)/2
        payoff += mass*((p0+p1)*(theta-g.cost)+2*g.complementarity*p0*p1)
        if theta == 1:
            freeze += conditional*(1-p0)*(1-p1)
    return dict(lending_rate=float(lending), lender_payoff=float(payoff), freeze_given_good=float(freeze))


def pure_baseline(g: Game) -> list[Vector]:
    return [np.array(p[0]+p[1], dtype=float) for p in equilibria(g)]
