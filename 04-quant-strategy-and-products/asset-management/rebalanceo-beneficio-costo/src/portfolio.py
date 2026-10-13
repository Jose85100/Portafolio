"""Long-only minimum variance and auditable, lagged cost-aware backtest."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class Config:
    window: int = 252
    step: int = 21
    cost_bps: float = 10.0
    gamma: float = 5.0
    shrink: float = 0.2

    def __post_init__(self):
        if self.window < 2 or self.step < 1:
            raise ValueError("invalid window/step")
        if not all(np.isfinite(x) for x in (self.cost_bps, self.gamma, self.shrink)):
            raise ValueError("nonfinite configuration")
        if self.cost_bps < 0 or self.gamma <= 0 or not 0 <= self.shrink <= 1:
            raise ValueError("invalid cost/gamma/shrink")


def minimum_variance(cov: np.ndarray, legacy: bool = False) -> np.ndarray:
    cov = np.asarray(cov, dtype=float)
    if (
        cov.ndim != 2
        or cov.shape[0] != cov.shape[1]
        or cov.shape[0] < 2
        or not np.isfinite(cov).all()
        or not np.allclose(cov, cov.T)
    ):
        raise ValueError("invalid covariance")
    if np.linalg.eigvalsh(cov).min() < -1e-12:
        raise ValueError("covariance not PSD")
    n = len(cov)
    scale = max(float(np.trace(cov) / n), 1e-15)
    objective = cov if legacy else cov / scale
    options = {} if legacy else {"ftol": 1e-12, "maxiter": 1000}
    result = minimize(
        lambda w: w @ objective @ w,
        np.full(n, 1 / n),
        jac=None if legacy else lambda w: 2 * objective @ w,
        bounds=[(0, 1)] * n,
        constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],
        method="SLSQP",
        options=options,
    )
    if not result.success:
        raise RuntimeError(result.message)
    w = result.x
    if abs(w.sum() - 1) > 1e-8 or w.min() < -1e-8:
        raise RuntimeError("infeasible optimizer output")
    # First-order gap for convex simplex QP; zero certifies global optimality.
    gap = float(w @ (2 * objective @ w) - np.min(2 * objective @ w))
    if not legacy and gap > 1e-5:
        raise RuntimeError(f"optimality gap {gap}")
    return w


def decide(current, target, cov, config):
    """Risk-only certainty-equivalent gain over next step, no alpha forecast."""
    turnover = float(np.abs(target - current).sum())  # two-way traded notional
    cost = config.cost_bps * 1e-4 * turnover
    gain = (
        config.gamma
        * config.step
        / 2
        * float(current @ cov @ current - target @ cov @ target)
    )
    return gain > cost, gain, cost


def simulate(seed=41, days=1260, regime="stationary"):
    if days <= 252 or regime not in ("stationary", "switch"):
        raise ValueError("invalid simulation")
    rng = np.random.default_rng(seed)
    vol = np.array([0.18, 0.15, 0.08, 0.10, 0.20]) / np.sqrt(252)
    mu = np.array([0.08, 0.07, 0.04, 0.05, 0.06]) / 252
    a = rng.uniform(-0.2, 0.6, (5, 5))
    corr = a @ a.T
    d = np.sqrt(np.diag(corr))
    corr /= np.outer(d, d)
    z = rng.standard_normal((days, 5))
    r = mu + z @ np.linalg.cholesky(np.outer(vol, vol) * corr).T
    if regime == "switch":
        changed_vol = vol[::-1]
        cut = days // 2
        r[cut:] = (
            mu
            + z[cut:] @ np.linalg.cholesky(np.outer(changed_vol, changed_vol) * corr).T
        )
    return r


def backtest(returns, strategy, config=None):
    config = Config() if config is None else config
    allowed = {
        "equal",
        "legacy_mv",
        "static_mv",
        "monthly_mv",
        "gate",
        "gate_no_shrink",
    }
    r = np.asarray(returns, dtype=float)
    if (
        strategy not in allowed
        or r.ndim != 2
        or r.shape[1] < 2
        or len(r) <= config.window
        or not np.isfinite(r).all()
        or (r <= -1).any()
    ):
        raise ValueError("invalid returns/strategy")
    w = np.full(r.shape[1], 1 / r.shape[1])
    static = (
        minimum_variance(np.cov(r[: config.window].T))
        if strategy == "static_mv"
        else None
    )
    net, gross, turnover, costs, weights, decisions = [], [], [], [], [], []
    for t in range(config.window, len(r)):
        rot = cost = 0.0
        if (t - config.window) % config.step == 0:
            cov = np.cov(r[t - config.window : t].T)
            if strategy == "gate":
                cov = (1 - config.shrink) * cov + config.shrink * np.diag(np.diag(cov))
            if strategy == "equal":
                target = np.full(len(w), 1 / len(w))
            elif strategy == "static_mv":
                target = static
            else:
                target = minimum_variance(cov, strategy == "legacy_mv")
            trade, gain, quoted_cost = decide(w, target, cov, config)
            if strategy not in ("gate", "gate_no_shrink"):
                trade = True
            if strategy == "static_mv" and t != config.window:
                trade = False
            if trade:
                rot = float(np.abs(target - w).sum())
                cost = quoted_cost
                w = target.copy()
            decisions.append(
                {
                    "day": t,
                    "trade": bool(trade),
                    "gain": gain,
                    "quoted_cost": quoted_cost,
                    "turnover": rot,
                }
            )
        weights.append(w.copy())
        g = float(w @ r[t])
        # Pay fees before returns: common convention for ALL baselines.
        net.append((1 - cost) * (1 + g) - 1)
        gross.append(g)
        turnover.append(rot)
        costs.append(cost)
        w = w * (1 + r[t]) / (1 + g)
    return {
        "net": np.array(net),
        "gross": np.array(gross),
        "turnover": np.array(turnover),
        "costs": np.array(costs),
        "weights": np.array(weights),
        "decisions": decisions,
    }


def metrics(result):
    r = result["net"]
    vol = float(r.std(ddof=1) * np.sqrt(252))
    wealth = np.r_[1.0, np.cumprod(1 + r)]
    downside = float(np.sqrt(np.mean(np.minimum(r, 0) ** 2)) * np.sqrt(252))
    return {
        "annual_return": float(np.mean(r) * 252),
        "volatility": vol,
        "sharpe": float(np.mean(r) * 252 / vol) if vol else 0.0,
        "sortino": float(np.mean(r) * 252 / downside) if downside else 0.0,
        "max_drawdown": float(np.min(wealth / np.maximum.accumulate(wealth) - 1)),
        "turnover": float(result["turnover"].sum()),
        "cost_drag_bps": float(result["costs"].sum() * 1e4),
        "terminal_wealth": float(wealth[-1]),
    }
