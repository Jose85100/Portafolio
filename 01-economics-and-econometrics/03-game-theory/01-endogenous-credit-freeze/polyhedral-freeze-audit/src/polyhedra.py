"""Exact rational product-polytope representation of the two-lender BNE set.

This exploits the affine, two-types-per-player payoff of the existing model.
It is not a generic equilibrium or high-dimensional vertex-enumeration solver.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'bayesian-freeze-audit/src'))
from game import Game  # noqa: E402

Point = tuple[F, F]
Row = tuple[F, F, F]  # a*x+b*y <= rhs, or equality
Pattern = tuple[int, int]


def dot(row: Row, point: Point) -> F:
    return row[0]*point[0]+row[1]*point[1]


@dataclass(frozen=True)
class Polygon:
    equalities: tuple[Row, ...]
    inequalities: tuple[Row, ...]
    vertices: tuple[Point, ...]

    def contains(self, point: Point) -> bool:
        return all(dot(r, point) == r[2] for r in self.equalities) and all(
            dot(r, point) <= r[2] for r in self.inequalities)

    @property
    def dimension(self) -> int:
        if not self.vertices:
            return -1
        origin = self.vertices[0]
        differences = [(v[0]-origin[0], v[1]-origin[1]) for v in self.vertices[1:]]
        if any(a[0]*b[1] != a[1]*b[0] for a, b in combinations(differences, 2)):
            return 2
        return int(any(a != (0, 0) for a in differences))


@dataclass(frozen=True)
class Cell:
    left: Polygon
    right: Polygon

    @property
    def dimension(self) -> int:
        return self.left.dimension+self.right.dimension

    @property
    def vertices(self) -> tuple[tuple[F, ...], ...]:
        return tuple(a+b for a, b in product(self.left.vertices, self.right.vertices))

    def contains_cell(self, other: 'Cell') -> bool:
        return all(self.left.contains(p) for p in other.left.vertices) and all(
            self.right.contains(p) for p in other.right.vertices)


def polygon(equalities: tuple[Row, ...], inequalities: tuple[Row, ...]) -> Polygon:
    """Enumerate vertices of a bounded 2D H-polytope, including segments/points.

    Input must include the unit box. Empty sets have no vertices, dimension -1.
    """
    box: tuple[Row, ...] = ((F(-1), F(0), F(0)), (F(1), F(0), F(1)),
                           (F(0), F(-1), F(0)), (F(0), F(1), F(1)))
    bounds = inequalities+box
    vertices: set[Point] = set()
    for a, b in combinations(equalities+bounds, 2):
        det = a[0]*b[1]-a[1]*b[0]
        if det == 0:
            continue
        p = ((a[2]*b[1]-a[1]*b[2])/det, (a[0]*b[2]-a[2]*b[0])/det)
        if all(dot(r, p) == r[2] for r in equalities) and all(dot(r, p) <= r[2] for r in bounds):
            vertices.add(p)
    return Polygon(equalities, bounds, tuple(sorted(vertices)))


def gains(g: Game) -> tuple[tuple[F, F, F], ...]:
    """Exact D_s = intercept + coeff0*x_other(0)+coeff1*x_other(1)."""
    pi, q, c, alpha = (F(str(v)) for v in (g.prior, g.accuracy, g.cost, g.complementarity))
    result = []
    for signal in (0, 1):
        l1, l0 = (q, 1-q) if signal else (1-q, q)
        post = pi*l1/(pi*l1+(1-pi)*l0)
        result.append((post-c, alpha*(post*(1-q)+(1-post)*q),
                       alpha*(post*q+(1-post)*(1-q))))
    return tuple(result)


def player_region(g: Game, own: Pattern, opponent: Pattern) -> Polygon:
    if any(v not in (0, 1, 2) for v in own+opponent):
        raise ValueError('Support values must be withdraw=0, lend=1 or indifferent=2')
    eq: list[Row] = []
    ub: list[Row] = []
    for k, v in enumerate(own):
        if v != 2:
            eq.append((F(k == 0), F(k == 1), F(v)))
    # Opponent's incentive constraints restrict this player's probabilities.
    for pattern, (b, a0, a1) in zip(opponent, gains(g)):
        if pattern == 2:
            eq.append((a0, a1, -b))
        elif pattern == 0:
            ub.append((a0, a1, -b))
        else:
            ub.append((-a0, -a1, b))
    return polygon(tuple(eq), tuple(ub))


def equilibrium_cells(g: Game, maximal: bool = True) -> list[Cell]:
    """Union of product cells covers all behavioral BNE of this specific game.

    Mixed supports are closed, so boundaries overlap. Maximal means containment-
    maximal among enumerated cells, NOT connected component or disjoint partition.
    """
    @lru_cache(maxsize=None)
    def region(a: Pattern, b: Pattern) -> Polygon:
        return player_region(g, a, b)

    patterns = tuple((a, b) for a, b in product((0, 1, 2), repeat=2))
    unique: dict[tuple[tuple[Point, ...], tuple[Point, ...]], Cell] = {}
    for a, b in product(patterns, repeat=2):
        left, right = region(a, b), region(b, a)
        if not left.vertices or not right.vertices:
            continue
        unique.setdefault((left.vertices, right.vertices), Cell(left, right))
    cells = list(unique.values())
    if maximal:
        cells = [c for i, c in enumerate(cells) if not any(
            j != i and d.dimension >= c.dimension and d.contains_cell(c) for j, d in enumerate(cells))]
    return sorted(cells, key=lambda c: (c.dimension, c.vertices))


def exact_regret(g: Game, x: tuple[F, ...]) -> F:
    if len(x) != 4 or any(v < 0 or v > 1 for v in x):
        raise ValueError('Four unit-interval probabilities required')
    coeff = gains(g)
    regrets = []
    for i, s in product((0, 1), repeat=2):
        b, a0, a1 = coeff[s]
        d = b+a0*x[2*(1-i)]+a1*x[2*(1-i)+1]
        regrets.append(max(F(0), d)-x[2*i+s]*d)
    return max(regrets)


def serialize_cell(cell: Cell) -> dict[str, object]:
    def serialize(poly: Polygon) -> dict[str, object]:
        return dict(dimension=poly.dimension,
                    equalities=[[str(v) for v in r] for r in poly.equalities],
                    inequalities=[[str(v) for v in r] for r in poly.inequalities],
                    vertices=[[str(v) for v in r] for r in poly.vertices])
    return dict(dimension=cell.dimension, left=serialize(cell.left), right=serialize(cell.right),
                vertices=[[str(v) for v in r] for r in cell.vertices])
