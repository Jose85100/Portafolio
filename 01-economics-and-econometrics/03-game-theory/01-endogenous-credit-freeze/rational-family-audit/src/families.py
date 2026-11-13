"""Gambit rational interchange and small exact compatibility-family reconstruction.

Restricted to the existing 2-player / 2-type game. Exponential biclique enumeration
is deliberately capped, not a general scalable Nash solver.
"""
from fractions import Fraction as F
from io import StringIO
from pathlib import Path
import sys
from typing import Any
import pygambit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'strategic-form-audit/src'))
from strategic import Game, Matrix, matrices, nfg

Point = tuple[F, F]
Hull = tuple[Point, ...]
Family = tuple[Hull, Hull]
Profile = tuple[tuple[F, ...], tuple[F, ...]]


def project(p: tuple[F, ...]) -> Point:
    if len(p) != 4 or any(v < 0 for v in p) or sum(p) != 1:
        raise ValueError('Four exact simplex probabilities required')
    return p[2]+p[3], p[1]+p[3]


def lift(x: Point) -> tuple[F, ...]:
    if len(x) != 2 or any(v < 0 or v > 1 for v in x):
        raise ValueError('Two unit-interval probabilities required')
    a, b = x
    return (1-a)*(1-b), (1-a)*b, a*(1-b), a*b


def regret(a: Matrix, b: Matrix, x: Point, y: Point) -> F:
    """Ex-ante deviation gain from direct payoff matrices, exact fractions."""
    p, q = lift(x), lift(y)
    row = tuple(sum(a[i][j]*q[j] for j in range(4)) for i in range(4))
    col = tuple(sum(p[i]*b[i][j] for i in range(4)) for j in range(4))
    return F(max(F(0), max(row)-sum(p[i]*row[i] for i in range(4)),
                 max(col)-sum(q[j]*col[j] for j in range(4))))


def cross(o: Point, a: Point, b: Point) -> F:
    return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])


def hull(points: tuple[Point, ...]) -> Hull:
    """Andrew monotone chain, with exact collinearity and canonical sorted output."""
    vertices = sorted(set(points))
    if len(vertices) <= 1:
        return tuple(vertices)
    chains = []
    for ordered in (vertices, list(reversed(vertices))):
        chain: list[Point] = []
        for p in ordered:
            while len(chain) >= 2 and cross(chain[-2], chain[-1], p) <= 0:
                chain.pop()
            chain.append(p)
        chains.extend(chain[:-1])
    return tuple(sorted(set(chains)))


def dimension(poly: Hull) -> int:
    return -1 if not poly else min(2, len(poly)-1)


def contains(outer: Family, inner: Family) -> bool:
    return all(hull(a+b) == a for a, b in zip(outer, inner))


def reconstruct(a: Matrix, b: Matrix, profiles: list[Profile], cap: int = 12) -> list[Family]:
    """Closed maximal bicliques of compatible projected marginal strategies.

    Each complete bipartite block generates product(conv(left), conv(right)).
    Completeness is conditional on the supplied external extreme enumeration;
    an empty/incomplete input does not acquire a completeness certificate here.
    """
    left = sorted({project(p) for p, _ in profiles})
    right = sorted({project(q) for _, q in profiles})
    if not left or not right:
        raise ValueError('No external equilibrium profiles supplied')
    if len(left) > cap or len(right) > cap:
        raise ValueError('Compatibility search cap exceeded')
    if any(regret(a, b, project(p), project(q)) != 0 for p, q in profiles):
        raise ValueError('External profile is not an exact equilibrium')
    neighbors = [{j for j, y in enumerate(right) if regret(a, b, x, y) == 0} for x in left]
    candidates: set[Family] = set()
    for mask in range(1, 1 << len(left)):
        selected = [i for i in range(len(left)) if mask & (1 << i)]
        common = set.intersection(*(neighbors[i] for i in selected))
        if not common:
            continue
        closure = [i for i, adjacent in enumerate(neighbors) if common <= adjacent]
        candidates.add((hull(tuple(left[i] for i in closure)), hull(tuple(right[j] for j in sorted(common)))))
    return sorted(c for c in candidates if not any(d != c and contains(d, c) for d in candidates))


def read_game(g: Game) -> Any:
    """Use Gambit's actual NFG parser, then verify all 32 exact payoffs."""
    game = pygambit.read_nfg(StringIO(nfg(g)))
    a, b = matrices(g)
    if len(game.players) != 2 or any(len(p.strategies) != 4 for p in game.players):
        raise ValueError('Unexpected external game dimensions')
    for i in range(4):
        for j in range(4):
            if (F(str(game[i, j][game.players[0]])), F(str(game[i, j][game.players[1]]))) != (a[i][j], b[i][j]):
                raise ValueError('Gambit payoff interchange mismatch')
    return game


def solve(g: Game) -> list[Profile]:
    game = read_game(g)
    result = pygambit.nash.enummixed_solve(game, rational=True)
    profiles = []
    for eq in result.equilibria:
        p = tuple(F(str(eq[s])) for s in game.players[0].strategies)
        q = tuple(F(str(eq[s])) for s in game.players[1].strategies)
        profiles.append((p, q))
    return profiles


def audit(g: Game) -> tuple[list[Profile], list[Family]]:
    profiles = solve(g)
    return profiles, reconstruct(*matrices(g), profiles)
