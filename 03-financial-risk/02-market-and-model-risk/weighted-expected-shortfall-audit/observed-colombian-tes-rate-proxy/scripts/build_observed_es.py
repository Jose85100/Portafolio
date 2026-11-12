#!/usr/bin/env python3
"""Apply the weighted ES engine to BanRep's Colombian TES 10Y yield factor."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "banrep_tes10_official.json"
REFERENCE_PATH = PROJECT_ROOT / "data" / "source_reference.json"
RESULTS = PROJECT_ROOT / "results"
FIGURES = PROJECT_ROOT / "figures"
PARENT_PROJECT = PROJECT_ROOT.parent
sys.path.insert(0, str(PARENT_PROJECT))
from src.tail import weighted_tail  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def independent_equal_mass(losses: np.ndarray, alpha: float) -> tuple[float, float, int, float]:
    """Independent order-statistic/integration implementation for equal masses."""
    ascending = sorted(float(x) for x in losses)
    descending = ascending[::-1]
    n = len(ascending)
    tail_n = (1.0 - alpha) * n
    if math.isclose(tail_n, round(tail_n), rel_tol=0.0, abs_tol=1e-10):
        tail_n = float(round(tail_n))
    whole = math.floor(tail_n)
    boundary = tail_n - whole
    numerator = math.fsum(descending[:whole])
    if boundary:
        numerator += boundary * descending[whole]
    var = ascending[min(math.ceil(alpha * n) - 1, n - 1)]
    return float(var), float(numerator / tail_n), whole, boundary


def load_source(path: Path, reference: dict) -> tuple[pd.DataFrame, str]:
    digest = sha256(path)
    if digest != reference["raw_sha256"]:
        raise ValueError(f"SHA-256 de fuente no coincide: {digest} != {reference['raw_sha256']}")
    if path.stat().st_size != reference["raw_bytes"]:
        raise ValueError(f"Bytes de fuente inesperados: {path.stat().st_size} != {reference['raw_bytes']}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("Se esperaba un arreglo JSON con una serie")
    series = payload[0]
    if series.get("id") != reference["series_id"] or series.get("nombre") != reference["series"]:
        raise ValueError("ID o nombre de serie no coincide con el manifiesto")
    if series.get("fuente") != "SEN y MEC, con cálculos Banco de la República.":
        raise ValueError(f"Fuente/método inesperados: {series.get('fuente')!r}")
    if series.get("unidadCorta") != "%" or series.get("descripcionPeriodicidad") != "Diaria":
        raise ValueError("Unidad o periodicidad de la serie cambió")
    points = series.get("data")
    if not isinstance(points, list) or len(points) != reference["observations"]:
        raise ValueError(f"Número de puntos inesperado: {len(points) if isinstance(points,list) else None}")
    colombia = timezone(timedelta(hours=-5))
    dates, yields = [], []
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError(f"Punto con esquema inesperado: {point!r}")
        timestamp_ms, yield_pct = point
        date = datetime.fromtimestamp(float(timestamp_ms) / 1000.0, tz=timezone.utc).astimezone(colombia).date()
        value = float(yield_pct)
        if not math.isfinite(value):
            raise ValueError(f"Yield no finito para {date}")
        dates.append(date)
        yields.append(value)
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("Fechas fuera de orden o duplicadas")
    observed_period = [dates[0].isoformat(), dates[-1].isoformat()]
    if observed_period != reference["period"]:
        raise ValueError(f"Periodo inesperado: {observed_period} != {reference['period']}")
    frame = pd.DataFrame({"date": pd.to_datetime(dates), "yield_pct": yields})
    return frame, digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Snapshot JSON oficial con hash fijado")
    args = parser.parse_args()
    input_path = args.input.expanduser().resolve()
    reference = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    frame, digest = load_source(input_path, reference)

    derivation = reference["transformation"]
    duration = float(derivation["modified_duration_years_assumed"])
    notional = float(derivation["notional_cop_assumed"])
    alpha = float(derivation["alpha"])
    frame["prior_date"] = frame["date"].shift(1)
    frame["yield_change_pct_point"] = frame["yield_pct"].diff()
    frame["yield_change_bp"] = frame["yield_change_pct_point"] * 100.0
    frame = frame.iloc[1:].copy().reset_index(drop=True)
    frame["calendar_gap_days"] = (frame["date"] - frame["prior_date"]).dt.days
    frame["loss_proxy_cop"] = duration * (frame["yield_change_bp"] / 10000.0) * notional
    frame["abs_yield_change_bp"] = frame["yield_change_bp"].abs()
    # Review flag only: this does not remove or alter any observations.
    frame["review_flag_gt_100bp"] = frame["abs_yield_change_bp"] > 100.0
    losses = frame["loss_proxy_cop"].to_numpy(dtype=float)
    result = weighted_tail(losses, alpha=alpha)
    var_independent, es_independent, whole, boundary = independent_equal_mass(losses, alpha)
    if not np.isclose(result.var, var_independent, rtol=0, atol=1e-7):
        raise AssertionError(f"VaR engine/manual mismatch: {result.var} != {var_independent}")
    if not np.isclose(result.es, es_independent, rtol=1e-12, atol=1e-7):
        raise AssertionError(f"ES engine/manual mismatch: {result.es} != {es_independent}")

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    output_csv = RESULTS / "colombian_tes_daily_proxy.csv"
    review = frame.sort_values("abs_yield_change_bp", ascending=False).head(20).copy()
    review["prior_yield_pct"] = review["yield_pct"] - review["yield_change_pct_point"]
    review[["prior_date", "date"]] = review[["prior_date", "date"]].apply(lambda column: column.dt.strftime("%Y-%m-%d"))
    review[["prior_date", "date", "prior_yield_pct", "yield_pct", "yield_change_bp", "calendar_gap_days", "loss_proxy_cop", "review_flag_gt_100bp"]].to_csv(
        RESULTS / "largest_yield_changes_for_review.csv", index=False, float_format="%.6f"
    )
    csv_frame = frame[["prior_date", "date", "yield_pct", "yield_change_pct_point", "yield_change_bp", "calendar_gap_days", "loss_proxy_cop", "review_flag_gt_100bp"]].copy()
    csv_frame["prior_date"] = csv_frame["prior_date"].dt.strftime("%Y-%m-%d")
    csv_frame["date"] = csv_frame["date"].dt.strftime("%Y-%m-%d")
    csv_frame.to_csv(output_csv, index=False, float_format="%.10f")

    tail_mass = round((1.0 - alpha) * len(frame), 10)
    summary = {
        "source": reference["source"],
        "series": reference["series"],
        "series_id": reference["series_id"],
        "source_url": reference["official_url"],
        "methodology_url": reference["methodology_url"],
        "source_method": reference["source_method"],
        "raw_sha256": digest,
        "raw_bytes": input_path.stat().st_size,
        "source_observations": len(frame) + 1,
        "yield_intervals": len(frame),
        "period": [frame["prior_date"].iloc[0].strftime("%Y-%m-%d"), frame["date"].iloc[-1].strftime("%Y-%m-%d")],
        "yield_unit": "percent per annum",
        "yield_change_unit": "basis points per consecutive observation",
        "duration_years_assumed": duration,
        "notional_cop_assumed": notional,
        "loss_proxy_formula": derivation["loss_proxy_formula"],
        "alpha": alpha,
        "scenario_probability": "equal per consecutive observed yield-change interval",
        "tail_mass_observations": tail_mass,
        "fully_included_worst_observations": whole,
        "fraction_of_next_boundary_observation": boundary,
        "var_loss_proxy_cop": result.var,
        "es_loss_proxy_cop": result.es,
        "independent_var_cop": var_independent,
        "independent_es_cop": es_independent,
        "engine_matches_independent_calculation": True,
        "max_calendar_gap_days": int(frame["calendar_gap_days"].max()),
        "intervals_with_gap_gt_3_days": int((frame["calendar_gap_days"] > 3).sum()),
        "review_flag_threshold_bp_not_excluded": 100.0,
        "intervals_flagged_for_manual_source_review": int(frame["review_flag_gt_100bp"].sum()),
        "top_10_abs_yield_changes_bp": [
            {"prior_date": str(row.prior_date.date()), "date": str(row.date.date()),
             "yield_change_bp": float(row.yield_change_bp), "loss_proxy_cop": float(row.loss_proxy_cop)}
            for row in frame.reindex(frame["abs_yield_change_bp"].nlargest(10).index).itertuples()
        ],
        "max_loss_proxy_cop": float(losses.max()),
        "mean_loss_proxy_cop": float(losses.mean()),
        "derived_csv_sha256": sha256(output_csv),
        "interpretation": "Empirical VaR/ES on a one-factor linear price-loss proxy for a hypothetical long TES exposure, not actual asset or portfolio P&L and not a backtest.",
        "limitations": [
            "The 10Y yield is a Nelson-Siegel zero-coupon curve point estimated by BanRep from SEN/MEC operations, not a specific bond total-return series.",
            "Duration and notional are scenario assumptions; the snapshot has no holdings, portfolio weights, hedge positions, actual P&L or model forecasts.",
            "Linear duration omits convexity, coupon cash flows, carry, roll-down, curve-shape/basis exposure, transaction costs and liquidity.",
            "Intervals are between consecutive published observations; calendar gaps vary and equal probability is assigned per interval without horizon adjustment.",
            "Historical empirical tail depends on the selected vintage and serial dependence; it is not a forecast or evidence of model calibration."
        ]
    }
    (RESULTS / "colombian_tes_es_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame([
        {"metric": "VaR", "alpha": alpha, "loss_proxy_cop": result.var},
        {"metric": "Expected Shortfall", "alpha": alpha, "loss_proxy_cop": result.es},
    ]).to_csv(RESULTS / "colombian_tes_es_metrics.csv", index=False, float_format="%.8f")

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    dates = pd.to_datetime(frame["date"])
    axes[0].plot(dates, frame["yield_pct"], color="#205b7a", lw=1.0)
    axes[0].set_title("BanRep TES cero cupón COP a 10 años · serie diaria")
    axes[0].set_ylabel("Rendimiento (%)")
    locator = mdates.AutoDateLocator(minticks=5, maxticks=9)
    axes[0].xaxis.set_major_locator(locator)
    axes[0].xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    axes[0].grid(axis="y", alpha=.2)
    worst = np.sort(losses)[::-1][:whole]
    axes[1].plot(np.arange(1, len(worst) + 1), worst / 1e6, color="#466f8d", lw=1.6)
    axes[1].axhline(result.var / 1e6, color="#cf8a34", ls="--", lw=2, label=f"VaR 97,5%: COP {result.var/1e6:,.1f} mill.")
    axes[1].axhline(result.es / 1e6, color="#a64f47", lw=2, label=f"ES 97,5% promedio: COP {result.es/1e6:,.1f} mill.")
    axes[1].set_title(f"Cola superior empírica (2,5%; {whole} intervalos) · D={duration:g} · nocional COP {notional/1e9:g} mil millones")
    axes[1].set_xlabel("Intervalo ordenado por pérdida (mayor a menor)")
    axes[1].set_ylabel("Pérdida proxy (COP millones)")
    axes[1].grid(axis="y", alpha=.2)
    axes[1].legend(frameon=False)
    fig.savefig(FIGURES / "colombian_tes_es_proxy.png", dpi=180, facecolor="white")
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
