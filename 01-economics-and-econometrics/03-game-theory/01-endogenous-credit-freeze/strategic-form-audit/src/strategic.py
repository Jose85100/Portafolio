"""Exact ex-ante strategic form and checked behavioral projection; two types only."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import numpy as np
from numpy.typing import NDArray

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'bayesian-freeze-audit/src'))
from game import Game, POLICIES

Matrix = tuple[tuple[F, ...], ...]


def matrices(g: Game) -> tuple[Matrix, Matrix]:
    """Direct latent-state sum, independent of the existing affine gain formula."""
    pi, q, c, alpha = (F(str(v)) for v in (g.prior, g.accuracy, g.cost, g.complementarity))
    left, right = [], []
    for a in POLICIES:
        row_a, row_b = [], []
        for b in POLICIES:
            ua = ub = F(0)
            for theta, s, t in product((0, 1), repeat=3):
                p = (pi if theta else 1-pi)*(q if s == theta else 1-q)*(q if t == theta else 1-q)
                ua += p*a[s]*(theta+alpha*b[t]-c)
                ub += p*b[t]*(theta+alpha*a[s]-c)
            row_a.append(ua)
            row_b.append(ub)
        left.append(tuple(row_a))
        right.append(tuple(row_b))
    return tuple(left), tuple(right)


def simplex(p: NDArray[np.float64]) -> NDArray[np.float64]:
    p = np.asarray(p, dtype=float)
    if p.shape != (4,) or not np.isfinite(p).all() or (p < -1e-10).any() or abs(p.sum()-1) > 1e-10:
        raise ValueError('Expected four finite simplex probabilities')
    return p


def project(p: NDArray[np.float64]) -> NDArray[np.float64]:
    """Marginals only; correlations between counterfactual types are not observed."""
    p = simplex(p)
    return p @ np.asarray(POLICIES, dtype=float)


def lift(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Independent-contingency representative; projection is many-to-one."""
    x = np.asarray(x, dtype=float)
    if x.shape != (2,) or not np.isfinite(x).all() or ((x < 0) | (x > 1)).any():
        raise ValueError('Expected two unit-interval probabilities')
    return np.array([np.prod([x[s] if a[s] else 1-x[s] for s in (0, 1)]) for a in POLICIES])


def strategic_regret(a: Matrix, b: Matrix, p: NDArray[np.float64], r: NDArray[np.float64]) -> float:
    p, r = simplex(p), simplex(r)
    aa, bb = np.asarray(a, float), np.asarray(b, float)
    return float(max(0., (aa @ r).max()-p @ aa @ r, (p @ bb).max()-p @ bb @ r))


def nfg(g: Game) -> str:
    """Gambit payoff .nfg: player one varies fastest; rational payoffs preserved."""
    a, b = matrices(g)
    payoffs = ' '.join(f'{a[i][j]} {b[i][j]}' for j in range(4) for i in range(4))
    return 'NFG 1 R "Bayesian credit freeze" { "Lender 0" "Lender 1" } { 4 4 }\n\n'+payoffs+'\n'


def parse_nfg(text: str) -> tuple[Matrix, Matrix]:
    """Strict reader for this exporter's fixed header; not a general NFG parser."""
    header, body = text.split('\n\n')
    expected = 'NFG 1 R "Bayesian credit freeze" { "Lender 0" "Lender 1" } { 4 4 }'
    if header != expected:
        raise ValueError('Unsupported header')
    values = [F(v) for v in body.split()]
    if len(values) != 32:
        raise ValueError('Expected 32 payoffs')
    return tuple(tuple(values[2*(4*j+i)] for j in range(4)) for i in range(4)), tuple(
        tuple(values[2*(4*j+i)+1] for j in range(4)) for i in range(4))
