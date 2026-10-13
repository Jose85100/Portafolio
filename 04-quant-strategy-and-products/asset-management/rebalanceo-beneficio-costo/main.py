"""Run the fixed-configuration synthetic benchmark; no parameter selection on results."""

import json
import platform
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.portfolio import Config, backtest, metrics, minimum_variance, simulate

ROOT = Path(__file__).resolve().parent
STRATEGIES = ["equal", "legacy_mv", "static_mv", "monthly_mv", "gate_no_shrink", "gate"]


def main():
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    config = Config()
    seeds = list(range(41, 61))
    rows, trajectories, decisions, timing = [], [], [], []
    start = time.perf_counter()
    for regime in ["stationary", "switch"]:
        for seed in seeds:
            r = simulate(seed, regime=regime)
            for cost in [0.0, 10.0, 50.0]:
                cfg = Config(cost_bps=cost)
                for strategy in STRATEGIES:
                    tick = time.perf_counter()
                    result = backtest(r, strategy, cfg)
                    elapsed = time.perf_counter() - tick
                    rows.append(
                        dict(
                            regime=regime,
                            seed=seed,
                            cost_bps=cost,
                            strategy=strategy,
                            seconds=elapsed,
                            **metrics(result),
                        )
                    )
                    if seed == 41 and cost == 10:
                        trajectories.append(
                            pd.DataFrame(
                                {
                                    "regime": regime,
                                    "strategy": strategy,
                                    "day": np.arange(cfg.window, len(r)),
                                    "net": result["net"],
                                    "gross": result["gross"],
                                    "turnover": result["turnover"],
                                    "cost": result["costs"],
                                }
                            )
                        )
                        decisions.extend(
                            dict(regime=regime, strategy=strategy, **d)
                            for d in result["decisions"]
                        )
    raw = pd.DataFrame(rows)
    raw.to_csv(out / "raw.csv", index=False)
    pd.concat(trajectories).to_csv(out / "daily.csv.gz", index=False)
    pd.DataFrame(decisions).to_csv(out / "decisions.csv", index=False)
    summary = (
        raw.groupby(["regime", "cost_bps", "strategy"])
        .mean(numeric_only=True)
        .drop(columns="seed")
    )
    summary.to_csv(out / "summary.csv")
    paired = []
    for regime in ["stationary", "switch"]:
        for cost in [0.0, 10.0, 50.0]:
            subset = raw[(raw.regime == regime) & (raw.cost_bps == cost)]
            for baseline in ["equal", "monthly_mv", "gate_no_shrink"]:
                for metric in ["sharpe", "volatility", "turnover", "terminal_wealth"]:
                    pivot = subset.pivot(
                        index="seed", columns="strategy", values=metric
                    )
                    delta = (pivot.gate - pivot[baseline]).to_numpy()
                    rng = np.random.default_rng(20261012)
                    boot = rng.choice(delta, (5000, len(delta)), replace=True).mean(
                        axis=1
                    )
                    paired.append(
                        {
                            "regime": regime,
                            "cost_bps": cost,
                            "baseline": baseline,
                            "metric": metric,
                            "mean_delta": delta.mean(),
                            "low": np.quantile(boot, 0.025),
                            "high": np.quantile(boot, 0.975),
                            "positive_fraction": (delta > 0).mean(),
                        }
                    )
    pd.DataFrame(paired).to_csv(out / "paired_bootstrap.csv", index=False)
    # Exact original DGP, seed and ten-year length; preserve legacy stdout separately.
    original = simulate(41, 2520)
    original_rows = [
        dict(strategy=s, **metrics(backtest(original, s, config))) for s in STRATEGIES
    ]
    pd.DataFrame(original_rows).to_csv(out / "repo_dgp.csv", index=False)
    covariance = np.cov(original[:252].T)
    eq = np.full(5, 0.2)
    diagnostics = []
    for legacy in [True, False]:
        w = minimum_variance(covariance, legacy)
        gradient = 2 * covariance @ w
        diagnostics.append(
            {
                "legacy": legacy,
                "weights": w.tolist(),
                "variance": float(w @ covariance @ w),
                "relative_variance": float(
                    (w @ covariance @ w) / (eq @ covariance @ eq)
                ),
                "daily_kkt_gap": float(w @ gradient - gradient.min()),
            }
        )
    (out / "solver_diagnostic.json").write_text(json.dumps(diagnostics, indent=2))
    # Scaling is measured on gated backtest only; tracemalloc is Python allocation peak, not RSS.
    for days in [630, 1260, 2520]:
        r = simulate(41, days)
        tracemalloc.start()
        tick = time.perf_counter()
        result = backtest(r, "gate")
        seconds = time.perf_counter() - tick
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        timing.append(
            {"days": days, "assets": 5, "seconds": seconds, "python_peak_bytes": peak}
        )
    pd.DataFrame(timing).to_csv(out / "scaling.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    for ax, regime in zip(axes, ["stationary", "switch"]):
        for strategy in STRATEGIES:
            series = next(
                x
                for x in trajectories
                if x.regime.iloc[0] == regime and x.strategy.iloc[0] == strategy
            )
            ax.plot(series.day, np.cumprod(1 + series.net), label=strategy)
        ax.set(
            title=f"{regime} · seed 41 · 10 bps",
            xlabel="Trading day",
            ylabel="Net wealth (initial = 1)",
        )
        ax.grid(alpha=0.2)
    axes[1].legend(fontsize=8)
    fig.savefig(out / "wealth.png", dpi=150)
    plt.close(fig)
    total = time.perf_counter() - start
    cpu = (
        next(
            (
                line.split(":", 1)[1].strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "unknown",
        )
        if Path("/proc/cpuinfo").exists()
        else platform.processor()
    )
    import scipy

    metadata = {
        "date": "2026-10-12 America/Bogota",
        "source_commit": "558bde13013df8a446fbb6acf4c69447be88dd03",
        "config": asdict(config),
        "seeds": seeds,
        "days": 1260,
        "regimes": ["stationary", "switch"],
        "costs_bps": [0, 10, 50],
        "runs": len(rows),
        "bootstrap_seed": 20261012,
        "bootstrap_replicates": 5000,
        "total_seconds": total,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pandas": pd.__version__,
        "os": platform.platform(),
        "cpu": cpu,
        "scope": "synthetic research prototype, not production",
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(summary.loc[("stationary", 10.0)].round(5).to_string())
    print(f"{len(rows)} executed runs; elapsed {total:.3f}s; results: {out}")


if __name__ == "__main__":
    main()
