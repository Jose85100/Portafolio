#!/usr/bin/env python3
"""Descriptive SFC regulatory-capital and accounting-impairment context."""
from __future__ import annotations

import hashlib
import json
import argparse
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "results"
FIG = ROOT / "figures"
PNL = DATA / "sfc_all_ec_non_ioe_pnl_snapshot.csv"
SOLVENCY_AGGREGATE = DATA / "sfc_solvency_aggregate_quarterly.csv"
SOLVENCY_AGGREGATE_SHA256 = "9b7360ba104dd336df12a2f06a49f4625c2f545c6f59a2abb60949ac5d25143b"
SOLVENCY_RESPONSE_SHA256 = "4da1af109c5f6f767dda5d015fd12ef1825c4dc28ef9ade07bdb46c1e00dd205"
PNL_SHA256 = "747a5de7bf8df97883f963b4f8bd20bb5e8e3b4a3cecf77ec34429b0ddea0e1f"
METADATA_SHA256 = "7f74655b7cff09c00f1d00b6fe56ed562ea167d3b2b5467781e1df35ee678133"
RISK_ROWS = {20: "technical_capital", 25: "credit_risk_weighted_assets", 30: "market_risk_weighted_amount", 32: "operational_risk_weighted_amount", 60: "reported_total_solvency_pct"}
ALLOWED_TYPES = {1, 2, 4, 32}  # banks, financial corps, financing companies, financial cooperatives


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate_solvency_records(raw: list[dict]) -> pd.DataFrame:
    """Aggregate temporary entity rows without persisting any identifying fields."""
    data = pd.DataFrame(raw)
    data["date"] = pd.to_datetime(data["fecha"])
    data["type"] = pd.to_numeric(data["tipo_entidad"], errors="raise").astype(int)
    data["entity_code"] = pd.to_numeric(data["codigo_entidad"], errors="raise").astype(int)
    data["item"] = pd.to_numeric(data["renglon"], errors="raise").astype(int)
    data["value"] = pd.to_numeric(data["valor"], errors="raise")
    data["created"] = pd.to_datetime(data[":created_at"], utc=True)
    data = data[data.type.isin(ALLOWED_TYPES)].copy()
    if set(data.item.unique()) != set(RISK_ROWS):
        raise ValueError("Unexpected capital line items in the SFC source response")
    key = ["date", "type", "entity_code", "item"]
    if data.duplicated(key).any():
        data = data.sort_values("created").drop_duplicates(key, keep="last")
    if data.duplicated(key).any() or not np.isfinite(data.value).all():
        raise ValueError("Duplicate records remain or source has non-finite values")
    panel = data.pivot(index=["date", "type", "entity_code"], columns="item", values="value")
    required = list(RISK_ROWS)
    complete = panel.dropna(subset=required).copy()
    complete["recalculated_entity_solvency_pct"] = 100 * complete[20] / (complete[25] + complete[30] + complete[32])
    row_diff = (complete["recalculated_entity_solvency_pct"] - complete[60]).abs()
    if (complete[[20, 25, 30, 32]].lt(0).any().any() or (complete[25] + complete[30] + complete[32]).le(0).any()):
        raise ValueError("Capital components must be nonnegative with positive risk-weighted denominator")
    if row_diff.max() > 0.02:
        raise ValueError(f"Institution-level source reconciliation failed; max abs difference {row_diff.max():.4f} pp")
    rows = []
    for date, all_entities in panel.groupby(level="date"):
        part = complete.xs(date, level="date")
        denom = part[25] + part[30] + part[32]
        rows.append({
            "period": date.strftime("%Y-%m"),
            "reporting_entities": int(len(all_entities)),
            "entities_with_all_capital_components": int(len(part)),
            "technical_capital_cop": float(part[20].sum()),
            "credit_risk_weighted_assets_cop": float(part[25].sum()),
            "market_risk_weighted_amount_cop": float(part[30].sum()),
            "operational_risk_weighted_amount_cop": float(part[32].sum()),
            "total_risk_weighted_denominator_cop": float(denom.sum()),
            "weighted_aggregate_total_solvency_pct": float(100 * part[20].sum() / denom.sum()),
            "median_entity_reported_total_solvency_pct": float(part[60].median()),
            "max_entity_ratio_reconciliation_abs_pp": float(row_diff.xs(date, level="date").max()),
        })
    result = pd.DataFrame(rows)
    if result.period.duplicated().any() or len(result) != 22:
        raise ValueError("Expected one aggregate row for each of the 22 quarterly cuts")
    return result


def fetch_and_verify_source(metadata: dict, expected_hash: str) -> pd.DataFrame:
    """Fetch source rows into memory, hash and aggregate, then discard the row-level response."""
    import requests
    response = None
    for attempt in range(3):
        try:
            response = requests.get(metadata["solvency_source"], params=metadata["solvency_query_parameters"], timeout=120)
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
            response.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))
    if response is None:
        raise RuntimeError("SFC source returned no response after retries")
    if hashlib.sha256(response.content).hexdigest() != expected_hash:
        raise ValueError("Live SFC response hash differs from the captured source; review updates before accepting a new snapshot")
    raw = response.json()
    if len(raw) != metadata["solvency_rows"]:
        raise ValueError("Live SFC row count differs from the captured response")
    # raw contains entity names/codes and is held only in memory for this call.
    result = aggregate_solvency_records(raw)
    del raw, response
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-source", action="store_true", help="Fetch SFC API rows transiently, hash and reaggregate in memory")
    args = parser.parse_args()
    if sha(PNL) != PNL_SHA256 or sha(SOLVENCY_AGGREGATE) != SOLVENCY_AGGREGATE_SHA256:
        raise ValueError("Source snapshot hash mismatch")
    metadata = json.loads((DATA / "source_manifest.json").read_text(encoding="utf-8"))
    if metadata["pnl_source_workbook_sha256"] != METADATA_SHA256:
        raise ValueError("SFC source workbook SHA-256 in the manifest does not match the approved snapshot")
    solv = pd.read_csv(SOLVENCY_AGGREGATE)
    if args.verify_source:
        live = fetch_and_verify_source(metadata, SOLVENCY_RESPONSE_SHA256)
        compare_cols = [c for c in solv.columns if c != "period"]
        if not np.allclose(live[compare_cols].to_numpy(float), solv[compare_cols].to_numpy(float), rtol=1e-10, atol=1e-6):
            raise ValueError("Live in-memory aggregate does not match the protected aggregate snapshot")
    row_diff = solv["max_entity_ratio_reconciliation_abs_pp"]
    pnl = pd.read_csv(PNL)
    if pnl.period.duplicated().any() or not pnl.period.is_monotonic_increasing:
        raise ValueError("P&L periods must be unique and ascending")
    for col in ["net_impairment_ytd_cop_millions", "net_profit_ytd_cop_millions"]:
        pnl[col] = pd.to_numeric(pnl[col], errors="raise")
    pnl["date"] = pd.to_datetime(pnl.period + "-01").dt.to_period("M")
    pnl = pnl[["date", "net_impairment_ytd_cop_millions", "net_profit_ytd_cop_millions"]]
    solv["date"] = pd.to_datetime(solv.period + "-01").dt.to_period("M")
    result = solv.merge(pnl, left_on="date", right_on="date", how="inner", validate="one_to_one")
    result = result.drop(columns=["date"])
    if len(result) != len(solv) or len(result) != 22:
        raise ValueError("Solvency and SFC P&L quarterly snapshots do not align completely")
    result["period_obj"] = pd.PeriodIndex(result.period, freq="M")
    impairment_ytd = dict(zip(result.period_obj, result.net_impairment_ytd_cop_millions))
    profit_ytd = dict(zip(result.period_obj, result.net_profit_ytd_cop_millions))
    q_impairment = []
    q_profit = []
    for p in result.period_obj:
        previous = p - 3
        if previous.year == p.year and previous in impairment_ytd:
            q_impairment.append(impairment_ytd[p] - impairment_ytd[previous])
            q_profit.append(profit_ytd[p] - profit_ytd[previous])
        else:
            q_impairment.append(impairment_ytd[p])
            q_profit.append(profit_ytd[p])
    result["net_impairment_expense_quarter_cop_millions"] = q_impairment
    result["net_profit_quarter_cop_millions"] = q_profit
    result = result.drop(columns=["period_obj"])
    result["net_impairment_ytd_cop"] = result.net_impairment_ytd_cop_millions * 1e6
    result["net_profit_ytd_cop"] = result.net_profit_ytd_cop_millions * 1e6
    result["net_impairment_expense_quarter_cop"] = result.net_impairment_expense_quarter_cop_millions * 1e6

    # External supervisory cross-check: BanRep reports 18.6% aggregate total solvency
    # for credit institutions at Sep-2024 (rounded to one decimal).
    sep24 = float(result.loc[result.period == "2024-09", "weighted_aggregate_total_solvency_pct"].iloc[0])
    if abs(sep24 - 18.6) >= 0.15:
        raise ValueError(f"Sep-2024 aggregate ratio does not reconcile to BanRep published 18.6%: {sep24:.4f}")

    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    result.to_csv(OUT / "quarterly_capital_and_impairment_context.csv", index=False, float_format="%.6f")
    latest = result.iloc[-1]
    summary = {
        "purpose": "Official aggregate context for regulatory solvency and accounting impairment; not an economic-capital estimate.",
        "scope": "Credit institutions excluding IOEs; solvency is aggregated from complete entity records, P&L is SFC's 'Todos los EC sin IOEs' series.",
        "period": [result.period.iloc[0], result.period.iloc[-1]],
        "quarters": len(result),
        "latest": {"period": latest.period,
                   "weighted_aggregate_total_solvency_pct": float(latest.weighted_aggregate_total_solvency_pct),
                   "technical_capital_cop_trillions": float(latest.technical_capital_cop / 1e12),
                   "net_impairment_expense_ytd_cop_trillions": float(latest.net_impairment_ytd_cop / 1e12),
                   "net_impairment_expense_quarter_cop_trillions": float(latest.net_impairment_expense_quarter_cop / 1e12),
                   "net_profit_ytd_cop_trillions": float(latest.net_profit_ytd_cop / 1e12),
                   "entities_with_complete_components": int(latest.entities_with_all_capital_components)},
        "independent_cross_check": {"period": "2024-09", "computed_aggregate_solvency_pct": sep24,
                                    "BanRep_published_aggregate_solvency_pct_rounded": 18.6},
        "source_sha256": {"sfc_solvency_api_response_ephemeral_hash": SOLVENCY_RESPONSE_SHA256,
                          "sfc_solvency_aggregate_snapshot": sha(SOLVENCY_AGGREGATE),
                          "sfc_pnl_extracted_csv": sha(PNL),
                          "sfc_pnl_source_workbook": METADATA_SHA256},
        "limitations": ["Net impairment expense is an accounting flow proxy net of recoveries, not a realized tail-loss distribution.",
                        "Solvency is a regulatory capital ratio; it does not identify expected loss, unexpected loss, VaR, or risk dependence.",
                        "No corporate/institutional exposure and loss-factor panel is observed; no portfolio-specific economic capital is inferred.",
                        "The SFC P&L snapshot is monthly year-to-date; this comparison selects quarter-end cumulative amounts and does not difference them into quarterly loss events.",
                        "Entities lacking one or more required capital components are excluded from that quarter's weighted ratio; counts are included in the output."]
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True, constrained_layout=True)
    dates = pd.to_datetime(result.period + "-01")
    axes[0].plot(dates, result.weighted_aggregate_total_solvency_pct, marker="o", color="#286a8e", lw=1.8)
    axes[0].set(title="Solvencia total agregada ponderada, EC sin IOEs", ylabel="Porcentaje")
    axes[0].grid(axis="y", alpha=.25)
    axes[1].plot(dates, result.net_impairment_expense_quarter_cop_millions / 1e6, marker="o", color="#c66542", lw=1.8)
    axes[1].axhline(0, color="#666", lw=.7)
    axes[1].set(title="Gasto neto trimestral por deterioro (diferencia de PyG acumulado)", ylabel="COP billones / trimestre", xlabel="Corte trimestral")
    axes[1].grid(axis="y", alpha=.25)
    fig.savefig(FIG / "solvency_and_impairment_context.png", dpi=170)
    plt.close(fig)
    qa = {"solvency_aggregate_rows_in_snapshot": len(solv), "periods": len(result),
          "complete_entity_periods": int(result.entities_with_all_capital_components.sum()),
          "partial_entity_periods_excluded": int((result.reporting_entities - result.entities_with_all_capital_components).sum()),
          "max_entity_ratio_reconciliation_abs_pp": float(row_diff.max()),
          "sha256": summary["source_sha256"],
          "online_source_verified": bool(args.verify_source),
          "checks": {"source_hashes_match": True, "pnl_solvency_quarter_join_complete": len(result) == 22,
                     "no_duplicate_quarterly_aggregate_period": not solv.period.duplicated().any(),
                     "institution_ratio_reconciliation_under_0_02pp": float(row_diff.max()) < 0.02,
                     "sep_2024_matches_banrep_18_6pct_within_0_15pp": abs(sep24 - 18.6) < 0.15}}
    qa["output_sha256"] = {
        str(path.relative_to(ROOT)): sha(path)
        for path in [OUT / "quarterly_capital_and_impairment_context.csv",
                     OUT / "summary.json", FIG / "solvency_and_impairment_context.png"]
    }
    (OUT / "qa_manifest.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"period": summary["period"], "latest": summary["latest"], "checks": qa["checks"], "sha256": qa["sha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
