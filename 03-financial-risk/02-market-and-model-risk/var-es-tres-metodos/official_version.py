"""Official-data application: Treasury 10Y yield-shock P&L proxy for VaR/ES.

This is an observed-data companion to the controlled method notebook. It is not
an actual bond total-return series or a production market-risk model.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

from main import historico, normal

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "official"
FIGURES = ROOT / "reports" / "figures"
SOURCE = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?page=0&type=daily_treasury_yield_curve"
TENOR = "10 Yr"
MODIFIED_DURATION = 8.0
NOTIONAL = 1_000_000.0
TRAINING = 500
HOLDOUT = 252


def load_observations() -> tuple[list[str], np.ndarray, list[dict[str, str]]]:
    rows: dict[str, float] = {}
    hashes = []
    for path in sorted(RAW.glob("daily-treasury-yield-curve-*.csv")):
        raw = path.read_bytes()
        hashes.append({"file": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if "Date" not in (reader.fieldnames or []) or TENOR not in (reader.fieldnames or []):
                raise ValueError(f"Unexpected source schema in {path.name}")
            for row in reader:
                date = row["Date"].strip()
                value = row[TENOR].strip()
                if not date or not value or value.upper() == "N/A":
                    continue
                parsed = __import__("datetime").datetime.strptime(date, "%m/%d/%Y").date().isoformat()
                numeric = float(value)
                if not math.isfinite(numeric) or parsed in rows:
                    raise ValueError(f"Invalid or duplicate observation at {parsed}")
                rows[parsed] = numeric
    dates = sorted(rows)
    yields_pct = np.array([rows[date] for date in dates], dtype=float)
    if len(dates) < TRAINING + 30:
        raise ValueError("Not enough clean yield observations for the declared holdout")
    return dates, yields_pct, hashes


def fitted_t(r: np.ndarray, level: float) -> tuple[float, float]:
    df, loc, scale = stats.t.fit(r)
    tail = 1 - level
    z = stats.t.ppf(tail, df)
    var = -(loc + scale * z)
    es_return = loc - scale * ((df + z * z) / (df - 1)) * stats.t.pdf(z, df) / tail
    return float(var), float(-es_return)


def method_estimates(r: np.ndarray, level: float) -> dict[str, tuple[float, float]]:
    hv = historico(r, level)
    nv = normal(r, level)
    tv = fitted_t(r, level)
    return {"historical": hv, "normal": nv, "student_t": tv}


def kupiec_pvalue(losses: np.ndarray, var: np.ndarray, tail: float) -> tuple[int, float]:
    hit = losses > var
    n = len(hit)
    x = int(hit.sum())
    if x == 0 or x == n:
        return x, 0.0
    phat = x / n
    lr = -2 * (math.log((1 - tail) ** (n - x) * tail**x) -
               math.log((1 - phat) ** (n - x) * phat**x))
    return x, float(stats.chi2.sf(lr, 1))


def run() -> dict:
    dates, yields_pct, hashes = load_observations()
    # First-order price return for a long position, using fixed modified duration.
    returns = -MODIFIED_DURATION * np.diff(yields_pct) / 100.0
    observation_dates = dates[1:]
    losses = -returns
    holdout_n = min(HOLDOUT, len(returns) - TRAINING)
    start = len(returns) - holdout_n
    if start < TRAINING:
        raise ValueError("Holdout leaves fewer than 500 observations for initial estimation")

    records = []
    forecast_rows = []
    for level in (0.95, 0.99):
        forecasts = {name: ([], []) for name in ("historical", "normal", "student_t")}
        for i in range(start, len(returns)):
            train = returns[i - TRAINING:i]
            estimates = method_estimates(train, level)
            for name, (var, es) in estimates.items():
                forecasts[name][0].append(var)
                forecasts[name][1].append(es)
                forecast_rows.append({"date": observation_dates[i], "level": level, "method": name,
                                      "loss_return": float(losses[i]), "var_return": var, "es_return": es,
                                      "exception": bool(losses[i] > var)})
        realized = losses[start:]
        for name, (var_list, es_list) in forecasts.items():
            var_arr = np.asarray(var_list)
            es_arr = np.asarray(es_list)
            exceptions, pvalue = kupiec_pvalue(realized, var_arr, 1 - level)
            records.append({"level": level, "method": name, "holdout_observations": holdout_n,
                            "exceptions": exceptions, "expected_exceptions": holdout_n * (1 - level),
                            "exception_rate": exceptions / holdout_n,
                            "kupiec_uc_pvalue": pvalue,
                            "mean_var_return": float(var_arr.mean()), "mean_es_return": float(es_arr.mean()),
                            "mean_exception_loss_return": float(realized[realized > var_arr].mean())
                            if exceptions else None})

    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    with (OUT / "rolling_backtest.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = list(forecast_rows[0])
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(forecast_rows)
    with (OUT / "backtest_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = list(records[0])
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)
    manifest = {"source": SOURCE, "source_provider": "U.S. Department of the Treasury",
                "series": "Daily Treasury Par Yield Curve Rates, 10 Yr", "yield_unit": "percent per annum",
                "source_files": hashes, "first_date": dates[0], "last_date": dates[-1],
                "yield_observations": len(dates), "daily_changes": len(returns),
                "modified_duration_assumption_years": MODIFIED_DURATION, "notional_usd": NOTIONAL,
                "initial_training_observations": TRAINING, "holdout_observations": holdout_n,
                "holdout_start": observation_dates[start], "holdout_end": observation_dates[-1],
                "limitations": ["constant-maturity par yield changes are a risk-factor proxy, not bond total returns",
                                "first-order duration P&L omits convexity, carry, roll-down, cash flows and basis risk",
                                "the holdout tests historical coverage with low power at 99 percent; it does not establish production fitness"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 4.7))
        date_axis = [datetime.strptime(date, "%Y-%m-%d") for date in observation_dates]
        ax.plot(date_axis, yields_pct[1:], color="#245b7a", linewidth=1.1)
        ax.set(title="U.S. Treasury 10-year par yield", ylabel="Percent per year", xlabel="Date")
        locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        fig.tight_layout()
        fig.savefig(FIGURES / "treasury-10y-yield-observed.png", dpi=170); plt.close(fig)
        backtest = [r for r in forecast_rows if r["level"] == 0.95]
        fig, ax = plt.subplots(figsize=(10, 4.7))
        x = [datetime.strptime(r["date"], "%Y-%m-%d") for r in backtest if r["method"] == "historical"]
        by_method = {m: [r for r in backtest if r["method"] == m] for m in ("historical", "normal", "student_t")}
        actual = np.asarray([r["loss_return"] for r in by_method["historical"]])
        ax.plot(x, actual * NOTIONAL, color="#17324d", linewidth=.9, label="Realized duration proxy")
        for method, color in (("historical", "#0f766e"), ("normal", "#d97706"), ("student_t", "#b91c1c")):
            ax.plot(x, np.asarray([r["var_return"] for r in by_method[method]]) * NOTIONAL,
                    linewidth=1, color=color, label=f"VaR 95% · {method}")
        ax.set(title="Rolling VaR versus observed 10-year yield-shock P&L proxy (95%)",
               ylabel="Loss / VaR (USD per USD 1m exposure)", xlabel="Holdout date")
        locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax.legend(ncol=2, fontsize=8); fig.tight_layout()
        fig.savefig(FIGURES / "treasury-10y-var-backtest-95.png", dpi=170); plt.close(fig)
    except ImportError:
        pass
    return {"manifest": manifest, "summary": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(json.dumps(run(), indent=2))
