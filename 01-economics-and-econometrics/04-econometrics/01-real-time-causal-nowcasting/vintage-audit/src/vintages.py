"""Release-ledger simulation and strictly as-of OLS evaluation."""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
from typing import Any
import numpy as np
from numpy.typing import NDArray

# Reuse the repository baseline instead of silently changing the estimator.
_CORE = Path(__file__).resolve().parents[4] / "computational-economics/src/econlab.py"
_spec = importlib.util.spec_from_file_location("econlab", _CORE)
assert _spec is not None and _spec.loader is not None
core: Any = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

@dataclass(frozen=True)
class Release:
    series: str
    event: int
    available: int
    value: float
    final: bool

@dataclass(frozen=True)
class Config:
    n: int = 240
    seed: int = 0
    delay: int = 1
    revision: float = 0.8
    rho: float = 0.7
    def __post_init__(self) -> None:
        if self.n < 80 or self.delay < 0 or not 0 <= self.revision or not abs(self.rho) < 1:
            raise ValueError("Invalid simulation configuration")
        if not np.isfinite([self.revision, self.rho]).all():
            raise ValueError("Nonfinite configuration")


def simulate(c: Config) -> tuple[list[Release], NDArray[np.float64]]:
    """x AR(1), final y=0.5+0.8*x+eps; preliminary noise is independent."""
    rng = np.random.default_rng(c.seed)
    x = np.zeros(c.n)
    shocks = rng.normal(size=c.n)
    for t in range(1, c.n):
        x[t] = c.rho*x[t-1] + shocks[t]
    y = 0.5+0.8*x+rng.normal(0, 0.3, c.n)
    xp = x+rng.normal(0, c.revision, c.n)
    yp = y+rng.normal(0, c.revision/2, c.n)
    rows = []
    for t in range(c.n):
        rows.extend([Release("x", t, t+c.delay, float(xp[t]), False),
                     Release("x", t, t+c.delay+3, float(x[t]), True),
                     Release("y", t, t+1, float(yp[t]), False),
                     Release("y", t, t+4, float(y[t]), True)])
    return rows, y


def snapshot(rows: list[Release], origin: int, revised: bool = False,
             ignore_delay: bool = False) -> dict[tuple[str, int], Release]:
    """Counterfactual toggles intentionally admit unavailable data; default never does."""
    result: dict[tuple[str, int], Release] = {}
    for r in rows:
        if r.event > origin:
            continue
        if revised:
            eligible = r.final and (ignore_delay or r.available-3 <= origin)
        else:
            eligible = r.available <= origin or (ignore_delay and not r.final)
        if not eligible:
            continue
        key = (r.series, r.event)
        if key not in result or r.available > result[key].available:
            result[key] = r
    return result


def forecast(rows: list[Release], origin: int, revised: bool = False,
             ignore_delay: bool = False, mean_only: bool = False) -> tuple[float, int]:
    snap = snapshot(rows, origin, revised, ignore_delay)
    # Every arm uses the same historical events, maturity >=4, and same origins.
    events = [t for t in range(origin-3) if ("x", t) in snap and ("y", t) in snap]
    if len(events) < 20:
        raise ValueError("Insufficient released training history")
    ys = [snap[("y", t)].value for t in events]
    if mean_only:
        return float(np.mean(ys)), 0
    xs = [snap[("x", t)].value for t in events]
    a, b = core.ols(xs, ys)
    latest = max(t for s, t in snap if s == "x")
    current = snap[("x", latest)]
    # Persistence fills the ragged edge; no unobserved current indicator is imputed from final data.
    prediction = a+b*current.value
    used = [snap[(s, t)] for t in events for s in ("x", "y")]+[current]
    violations = sum(r.available > origin for r in used)
    return float(prediction), violations


def evaluate(c: Config) -> list[dict[str, Any]]:
    rows, y = simulate(c)
    out = []
    arms = [("asof_ols", False, False, False),
            ("final_with_delay", True, False, False),
            ("ignore_delay", False, True, False),
            ("final_no_delay", True, True, False),
            ("released_mean", False, False, True)]
    for name, rev, delay, mean in arms:
        for origin in range(60, c.n):
            pred, violations = forecast(rows, origin, rev, delay, mean)
            out.append(dict(seed=c.seed, n=c.n, delay=c.delay, revision=c.revision,
                            arm=name, origin=origin, target=float(y[origin]),
                            prediction=pred, squared_error=float((pred-y[origin])**2),
                            violations=violations))
    return out
