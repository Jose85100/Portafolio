"""Finite two-lender Bayesian coordination game; exhaustive pure BNE audit."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import importlib.util
import math
from pathlib import Path
from typing import Any

Policy = tuple[int, int]
Profile = tuple[Policy, Policy]
POLICIES: tuple[Policy, ...] = ((0, 0), (0, 1), (1, 0), (1, 1))
PROFILES: tuple[Profile, ...] = tuple((a, b) for a in POLICIES for b in POLICIES)
_spec = importlib.util.spec_from_file_location("econlab", Path(__file__).resolve().parents[4] /
                                              "computational-economics/src/econlab.py")
assert _spec is not None and _spec.loader is not None
core: Any = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

@dataclass(frozen=True)
class Game:
    prior: float = 0.5
    accuracy: float = 0.8
    cost: float = 0.9
    complementarity: float = 0.8
    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.prior, self.accuracy, self.cost, self.complementarity)):
            raise ValueError("Parameters must be finite")
        if not 0 < self.prior < 1 or not 0.5 <= self.accuracy <= 1 or self.cost < 0 or self.complementarity < 0:
            raise ValueError("Invalid parameters")


def posterior(g: Game, signal: int) -> float:
    if signal not in (0, 1):
        raise ValueError("Signal must be binary")
    likelihood1 = g.accuracy if signal else 1-g.accuracy
    likelihood0 = 1-g.accuracy if signal else g.accuracy
    return g.prior*likelihood1/(g.prior*likelihood1+(1-g.prior)*likelihood0)


def gain(g: Game, signal: int, other: Policy) -> float:
    """Interim utility of lending minus withdrawing; conditional signals independent."""
    post = posterior(g, signal)
    lend1 = (1-g.accuracy)*other[0]+g.accuracy*other[1]
    lend0 = g.accuracy*other[0]+(1-g.accuracy)*other[1]
    return post + g.complementarity*(post*lend1+(1-post)*lend0)-g.cost


def regret(g: Game, profile: Profile) -> float:
    return max(0., *( (1-2*profile[i][s])*gain(g,s,profile[1-i]) for i in (0,1) for s in (0,1)))


def equilibria(g: Game, tolerance: float = 1e-12) -> list[Profile]:
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("Invalid tolerance")
    return [p for p in PROFILES if regret(g,p) <= tolerance]


def exact_equilibria(g: Game) -> list[Profile]:
    """Independent rational oracle: direct enumeration of latent state and other signal."""
    pi,q,c,a = [Fraction(str(v)) for v in (g.prior,g.accuracy,g.cost,g.complementarity)]
    result = []
    for profile in PROFILES:
        valid = True
        for i,s in product((0,1),repeat=2):
            delta = Fraction(0)
            for theta,t in product((0,1),repeat=2):
                prob = (pi if theta else 1-pi)*(q if s==theta else 1-q)*(q if t==theta else 1-q)
                delta += prob*(theta+a*profile[1-i][t]-c)
            if (1-2*profile[i][s])*delta > 0:
                valid = False
        if valid:
            result.append(profile)
    return result


def best_response(g: Game, other: Policy) -> Policy:
    return (int(core.best_response_grid(lambda action: action*gain(g,0,other),[0,1])),
            int(core.best_response_grid(lambda action: action*gain(g,1,other),[0,1])))


def iterate(g: Game, start: Profile = ((0,0),(0,0)), limit: int = 50) -> tuple[Profile | None, int]:
    if limit < 1:
        raise ValueError("Positive iteration limit required")
    visited: set[Profile] = set()
    current = start
    for step in range(1,limit+1):
        nxt = (best_response(g,current[1]),best_response(g,current[0]))
        if nxt == current:
            return current,step
        if nxt in visited:
            return None,step
        visited.add(current)
        current = nxt
    return None,limit


def outcomes(g: Game, profile: Profile) -> dict[str,float]:
    """Exact finite-state probabilities; payoff excludes borrower/social welfare."""
    lending = payoff = freeze_good = 0.
    for theta,s0,s1 in product((0,1),repeat=3):
        conditional = (g.accuracy if s0==theta else 1-g.accuracy)*(g.accuracy if s1==theta else 1-g.accuracy)
        mass = (g.prior if theta else 1-g.prior)*conditional
        a0,a1 = profile[0][s0],profile[1][s1]
        lending += mass*(a0+a1)/2
        payoff += mass*(a0*(theta+g.complementarity*a1-g.cost)+a1*(theta+g.complementarity*a0-g.cost))
        if theta==1 and a0==a1==0:
            freeze_good += conditional
    return dict(lending_rate=lending,lender_payoff=payoff,freeze_given_good=freeze_good)
