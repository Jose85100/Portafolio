#!/usr/bin/env python3
"""Rolling historical/Gaussian VaR backtest on BanRep Colombian TES 10Y shocks.

This is a one-factor duration P&L proxy, not bond total return or portfolio P&L.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

ROOT = Path(__file__).resolve().parent
VAR_PROJECT = ROOT.parent / "var-es-tres-metodos"
ES_COMPANION = ROOT.parent / "weighted-expected-shortfall-audit" / "observed-colombian-tes-rate-proxy"
sys.path.insert(0, str(VAR_PROJECT))
sys.path.insert(0, str(ES_COMPANION / "scripts"))
from build_observed_es import load_source  # noqa: E402
from main import historico  # noqa: E402

REFERENCE = json.loads((ES_COMPANION / "data" / "source_reference.json").read_text(encoding="utf-8"))
RAW = ES_COMPANION / "data" / "raw" / "banrep_tes10_official.json"
TRAINING = 1000
HOLDOUT_START = pd.Timestamp("2019-01-01")
DURATION_YEARS = 8.0
NOTIONAL_COP = 1_000_000_000.0
LEVELS = (0.95, 0.975, 0.99)
OUT = ROOT / "data" / "official" / "colombian_tes"
FIGURES = ROOT / "reports" / "figures"


def log_likelihood(probability: float, n0: int, n1: int) -> float:
    p = min(max(float(probability), 1e-12), 1 - 1e-12)
    return n0 * math.log1p(-p) + n1 * math.log(p)


def coverage_diagnostics(hit: np.ndarray, tail: float) -> dict:
    n = len(hit)
    k = int(hit.sum())
    p_hat = k / n
    lr_uc = max(0.0, -2 * (log_likelihood(tail, n-k, k) - log_likelihood(p_hat, n-k, k)))
    n00 = n01 = n10 = n11 = 0
    for previous, current in zip(hit[:-1], hit[1:]):
        if previous == 0 and current == 0: n00 += 1
        elif previous == 0 and current == 1: n01 += 1
        elif previous == 1 and current == 0: n10 += 1
        else: n11 += 1
    total_transitions = n00 + n01 + n10 + n11
    pooled = (n01 + n11) / total_transitions if total_transitions else p_hat
    p01 = n01 / (n00 + n01) if n00 + n01 else pooled
    p11 = n11 / (n10 + n11) if n10 + n11 else pooled
    lr_ind = max(0.0, -2 * (log_likelihood(pooled, n00+n10, n01+n11)
                           - log_likelihood(p01, n00, n01)
                           - log_likelihood(p11, n10, n11)))
    return {"holdout_observations": n, "exceptions": k,
            "expected_exceptions": n * tail, "exception_rate": p_hat,
            "kupiec_uc_lr": lr_uc, "kupiec_uc_pvalue": float(chi2.sf(lr_uc, 1)),
            "christoffersen_ind_lr": lr_ind,
            "christoffersen_ind_pvalue": float(chi2.sf(lr_ind, 1)),
            "transition_counts": {"n00": n00, "n01": n01, "n10": n10, "n11": n11}}


def main() -> None:
    source, digest = load_source(RAW, REFERENCE)
    source["prior_date"] = source.date.shift(1)
    source["yield_change_bp"] = source.yield_pct.diff() * 100.0
    source = source.iloc[1:].copy().reset_index(drop=True)
    source["calendar_gap_days"] = (source.date - source.prior_date).dt.days
    # First-order return approximation for a long fixed-duration TES exposure.
    returns = -DURATION_YEARS * source.yield_change_bp.to_numpy() / 10_000.0
    losses = -returns
    dates = source.date.to_numpy()
    holdout_index = int(np.searchsorted(dates, HOLDOUT_START.to_datetime64(), side="left"))
    if holdout_index < TRAINING or len(returns) - holdout_index < 100:
        raise ValueError("Holdout must leave at least 1000 estimation intervals and 100 evaluation intervals")

    rows, forecasts = [], {level: [] for level in LEVELS}
    for i in range(holdout_index, len(returns)):
        training_returns = returns[i-TRAINING:i]
        mean = float(training_returns.mean())
        sd = float(training_returns.std(ddof=1))
        if not math.isfinite(sd) or sd <= 0:
            raise ValueError(f"Invalid training volatility before {source.date.iloc[i].date()}")
        for level in LEVELS:
            historical_var, _ = historico(training_returns, level)
            gaussian_var = -(mean + sd * norm.ppf(1-level))
            for method, var in (("historical", historical_var), ("gaussian", gaussian_var)):
                loss = float(losses[i])
                hit = bool(loss > var)
                row = {"date": source.date.iloc[i].date().isoformat(), "level": level,
                       "method": method, "loss_return_proxy": loss,
                       "var_return_proxy": float(var), "exception": hit,
                       "loss_proxy_cop": loss * NOTIONAL_COP,
                       "var_proxy_cop": float(var) * NOTIONAL_COP,
                       "yield_change_bp": float(source.yield_change_bp.iloc[i]),
                       "calendar_gap_days": int(source.calendar_gap_days.iloc[i]),
                       "manual_review_flag_abs_change_gt_100bp": bool(abs(source.yield_change_bp.iloc[i]) > 100)}
                rows.append(row)
                forecasts[level].append((method, hit, loss, float(var)))

    records = []
    for level in LEVELS:
        for method in ("historical", "gaussian"):
            selected = [row for row in rows if row["level"] == level and row["method"] == method]
            hit = np.array([row["exception"] for row in selected], dtype=int)
            diagnostics = coverage_diagnostics(hit, 1-level)
            realized = np.array([row["loss_return_proxy"] for row in selected])
            vars_ = np.array([row["var_return_proxy"] for row in selected])
            diagnostics.update({"method": method, "confidence_level": level,
                                "mean_var_proxy_cop": float(vars_.mean() * NOTIONAL_COP),
                                "mean_realized_loss_proxy_cop": float(realized.mean() * NOTIONAL_COP),
                                "source_exceptions_over_100bp": int(sum(r["exception"] and r["manual_review_flag_abs_change_gt_100bp"] for r in selected))})
            records.append(diagnostics)

    OUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "rolling_backtest.csv", index=False, float_format="%.10f")
    summary = {"source": REFERENCE["source"], "series": REFERENCE["series"],
               "source_url": REFERENCE["official_url"], "source_methodology_url": REFERENCE["methodology_url"],
               "raw_sha256": digest, "source_period": REFERENCE["period"],
               "holdout_start_date": rows[0]["date"],
               "holdout_end_date": rows[-1]["date"], "estimation_window_intervals": TRAINING,
               "holdout_observation_intervals": records[0]["holdout_observations"],
               "levels": list(LEVELS), "methods": ["historical", "gaussian"],
               "modified_duration_years_assumed": DURATION_YEARS,
               "notional_cop_assumed": NOTIONAL_COP,
               "intervals_with_abs_yield_change_gt_100bp_in_holdout": int(source.iloc[holdout_index:].yield_change_bp.abs().gt(100).sum()),
               "metrics": records,
               "scope": "One-factor, first-order fixed-duration P&L proxy on the BanRep COP TES 10Y yield curve; not a specific TES bond return, portfolio P&L, or production VaR validation.",
               "limitations": ["BanRep's yield is an estimated Nelson-Siegel zero-coupon curve point, not total return.",
                               "Duration and notional are assumptions; convexity, carry, roll-down, curve shape, basis, liquidity, and transaction costs are omitted.",
                               "Historical source anomalies before the holdout are not adjudicated by this test; see the source companion. Holdout observations over 100 bp are flagged and retained.",
                               "Exception tests have limited power and p-values are diagnostics, not acceptance criteria.",
                               "No actual positions, forecast record, institutional limits, or realized portfolio P&L are available."]}
    (OUT / "backtest_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    frame = pd.DataFrame(rows)
    selected = frame[(frame.level == 0.975) & (frame.method == "historical")].copy()
    x = pd.to_datetime(selected.date)
    realized = selected.loss_proxy_cop / 1e6
    var = selected.var_proxy_cop / 1e6
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(x, realized, color="#183b56", lw=0.8, label="Pérdida realizada proxy")
    ax.plot(x, var, color="#bc4749", lw=1.0, label="VaR histórico rolling 97,5%")
    hits = selected.exception.to_numpy(dtype=bool)
    ax.scatter(x[hits], realized.to_numpy()[hits], color="#f0a202", s=24, zorder=3, label="Excepción")
    locator = mdates.AutoDateLocator(minticks=5, maxticks=9)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.set(title="BanRep TES COP 10 años: backtest de VaR sobre shock de tasa (97,5%)",
           ylabel="COP millones · duración 8 · nocional COP 1.000 millones",
           xlabel="Retención fuera de muestra desde 2019")
    ax.grid(axis="y", alpha=.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "colombian-tes-var-backtest.png", dpi=170, facecolor="white")
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
