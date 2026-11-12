#!/usr/bin/env python3
"""Observed-factor hedge-ratio sensitivities for purely hypothetical positions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_ROUTE = ROOT.parent.parent / "02-fx-interest-rate-exposure/observed-banrep-sensitivity"
TRM = SOURCE_ROUTE / "data/trm-banrep-series-id-1-snapshot-2026-11-11.json"
DTF = ROOT.parents[4] / "04-quant-strategy-and-products/treasury-and-alm/sensibilidad-fondeo-dtf/data/dtf_monthly_derived.csv"
INPUT_OUTPUT = SOURCE_ROUTE / "results/monthly_factor_sensitivities.csv"
OUT = ROOT / "results"
FIG = ROOT / "figures"
TRM_SHA256 = "d5068f3801b18a5530d291d6a2d0587e5ceb580d52879de5ae363168999edf77"
DTF_SHA256 = "56e4e436cd7add0aac50dd8e1c29007fa173ed8e07e4b484633d19faa33c79ec"
BASELINE_SHA256 = "67b58ed41b2310d27a74ff8cfc6aa54cdd3d307180e5b9bcab51cbfdd1756b14"
USD_POSITION = 1_000_000
COP_FLOATING_BALANCE = 100_000_000_000
HEDGE_RATIOS = (0.0, 0.5, 0.8, 1.0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha(TRM) != TRM_SHA256 or sha(DTF) != DTF_SHA256:
        raise ValueError("Source hash mismatch; review and version new official snapshots before rebuilding")
    # Re-run the documented source companion first to create the deterministic joined baseline.
    import runpy
    runpy.run_path(str(SOURCE_ROUTE / "run_observed_sensitivity.py"), run_name="__main__")
    if BASELINE_SHA256 and sha(INPUT_OUTPUT) != BASELINE_SHA256:
        raise ValueError("Joined baseline output hash mismatch")
    frame = pd.read_csv(INPUT_OUTPUT, parse_dates=["fecha", "mes"])
    needed = {"mes", "fx_revaluation_change_cop", "dtf_annualized_cost_change_cop"}
    if not needed.issubset(frame.columns) or frame.mes.duplicated().any() or not frame.mes.is_monotonic_increasing:
        raise ValueError("Joined factor frame failed schema or period QA")
    if frame.fx_revaluation_change_cop.isna().sum() != 1 or frame.dtf_annualized_cost_change_cop.isna().sum() != 0:
        raise ValueError("Unexpected missingness in first differences / 12-month changes")

    # Positive values mean additional cost. Hedge scenario is assumed to offset a share
    # of the same observed factor shock at 100% effectiveness and zero cost/basis.
    base = frame[["mes", "fx_revaluation_change_cop", "dtf_annualized_cost_change_cop"]].copy()
    base["fx_unhedged_cost_change_cop_millions"] = base.fx_revaluation_change_cop / 1e6
    base["dtf_unhedged_annualized_cost_change_cop_millions"] = base.dtf_annualized_cost_change_cop / 1e6
    rows = []
    for factor, col, position, unit in [
        ("fx_usd_liability", "fx_unhedged_cost_change_cop_millions", USD_POSITION, "COP millions / month"),
        ("dtf_floating_interest", "dtf_unhedged_annualized_cost_change_cop_millions", COP_FLOATING_BALANCE, "COP millions / year annualized"),
    ]:
        x = base[col].dropna().to_numpy(float)
        for ratio in HEDGE_RATIOS:
            residual = x * (1.0 - ratio)
            rows.append({
                "factor": factor, "hedge_ratio_pct": ratio * 100,
                "observations": int(len(x)), "position_assumption": position,
                "unit": unit, "mean_cost_change": float(np.mean(residual)),
                "volatility_cost_change_sample_sd": float(np.std(residual, ddof=1)),
                "p95_cost_change": float(np.quantile(residual, .95)),
                "worst_observed_adverse_cost_change": float(max(0.0, np.max(residual))),
                "observed_max_cost_saving_change": float(min(0.0, np.min(residual))),
                "scenario_assumptions": "perfect same-factor offset; zero transaction cost, basis risk, collateral and ineffectiveness",
            })
    scenarios = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    scenarios.to_csv(OUT / "hedge_ratio_sensitivities.csv", index=False, float_format="%.6f")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), constrained_layout=True)
    for ax, factor, title, ylabel in [
        (axes[0], "fx_usd_liability", "USD liability", "COP millions / month"),
        (axes[1], "dtf_floating_interest", "DTF-indexed balance", "COP millions / year, annualized"),
    ]:
        group = scenarios[scenarios.factor == factor]
        ax.plot(group.hedge_ratio_pct, group.worst_observed_adverse_cost_change,
                marker="o", linewidth=2, color="#2b708e")
        ax.set(title=title, xlabel="Illustrative same-factor offset (%)", ylabel=ylabel)
        ax.set_xticks([0, 50, 80, 100])
        ax.grid(alpha=.25)
    fig.suptitle("Observed adverse cost sensitivity under idealized hedge offsets")
    fig.savefig(FIG / "hedge_ratio_sensitivity.png", dpi=170)
    plt.close(fig)

    # Summarize the latest observation and risk-reduction metrics relative to no hedge.
    summaries = []
    for factor, group in scenarios.groupby("factor", sort=False):
        zero = float(group.loc[group.hedge_ratio_pct == 0, "volatility_cost_change_sample_sd"].iloc[0])
        for _, r in group.iterrows():
            summaries.append({"factor": factor, "hedge_ratio_pct": r.hedge_ratio_pct,
                              "volatility_reduction_pct": None if zero == 0 else 100*(1-float(r.volatility_cost_change_sample_sd)/zero),
                              "p95_cost_change": float(r.p95_cost_change),
                              "worst_adverse_cost_change": float(r.worst_observed_adverse_cost_change),
                              "unit": r.unit})
    summary = {
        "purpose": "Historical observed-factor sensitivity for hypothetical positions and idealized hedge offsets; not a validated optimization or hedge recommendation.",
        "source_sha256": {"trm_snapshot": sha(TRM), "dtf_derived_snapshot": sha(DTF), "joined_baseline_csv": sha(INPUT_OUTPUT)},
        "period": [base.mes.min().strftime("%Y-%m"), base.mes.max().strftime("%Y-%m")],
        "positions": {"usd_liability": USD_POSITION, "cop_dtf_floating_balance": COP_FLOATING_BALANCE},
        "hedge_ratios_pct": [r*100 for r in HEDGE_RATIOS],
        "scenario_design": "Linear offset of observed factor cost shock; constant notional; 100% same-factor effectiveness; zero cost, basis, collateral, liquidity and accounting effects.",
        "metrics": summaries,
        "limitations": ["FX and DTF metrics are separate and cannot be summed into joint loss.", "Historical shock rows are not forecast distributions and ratio grid is not an optimization.", "No institution exposure, derivative trade, hedge price, hedge effectiveness, or accounting outcome is observed.", "DTF cost changes are annualized repricing sensitivities, not monthly realized interest cash flows."],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    qa = {"source_sha256": summary["source_sha256"], "periods": len(base),
          "fx_nonmissing": int(base.fx_unhedged_cost_change_cop_millions.notna().sum()),
          "dtf_nonmissing": int(base.dtf_unhedged_annualized_cost_change_cop_millions.notna().sum()),
          "scenario_rows": len(scenarios), "ratios": [r*100 for r in HEDGE_RATIOS],
          "checks": {"expected_scenario_rows": len(scenarios) == 8,
                     "zero_hedge_matches_baseline": bool(np.isclose(scenarios[scenarios.hedge_ratio_pct == 0].volatility_cost_change_sample_sd.iloc[0], np.std(base.fx_unhedged_cost_change_cop_millions.dropna(), ddof=1))),
                     "full_hedge_residuals_zero": bool(np.allclose(scenarios[scenarios.hedge_ratio_pct == 100][["mean_cost_change", "volatility_cost_change_sample_sd", "p95_cost_change", "worst_observed_adverse_cost_change"]].to_numpy(), 0))}}
    (OUT / "qa_manifest.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"period": summary["period"], "sha256": summary["source_sha256"], "qa": qa["checks"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
