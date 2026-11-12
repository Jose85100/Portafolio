#!/usr/bin/env python3
"""Apply the weighted ES engine to an official Treasury-rate P&L proxy."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PROJECT_ROOT = HERE.parent
DEFAULT_INPUT = REPO_ROOT / "03-financial-risk/02-market-and-model-risk/pruebas-de-estres-escenarios/data/official/daily_rate_shocks.csv"
REFERENCE_PATH = HERE / "data" / "source_reference.json"
OUTPUT = HERE / "results"
FIGURES = HERE / "figures"
sys.path.insert(0, str(PROJECT_ROOT))
from src.tail import weighted_tail  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_proxy(path: Path, reference: dict) -> pd.DataFrame:
    actual_hash = sha256_file(path)
    if actual_hash != reference["derived_input_sha256"]:
        raise ValueError(f"SHA-256 no coincide: {actual_hash} != {reference['derived_input_sha256']}")
    data = pd.read_csv(path)
    expected_columns = {"date", "yield_change_bp", "long_bond_loss_usd", "long_bond_loss_pct_notional"}
    if expected_columns - set(data.columns):
        raise ValueError(f"Faltan columnas requeridas: {sorted(expected_columns - set(data.columns))}")
    if len(data) != reference["derived_input_rows"]:
        raise ValueError(f"Filas inesperadas: {len(data)} != {reference['derived_input_rows']}")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    if data["date"].isna().any() or data["date"].duplicated().any():
        raise ValueError("Fechas inválidas o duplicadas")
    for column in ["yield_change_bp", "long_bond_loss_usd", "long_bond_loss_pct_notional"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not np.isfinite(data[column].to_numpy(dtype=float)).all():
            raise ValueError(f"Valores no finitos/no numéricos en {column}")

    derivation = reference["derivation"]
    implied_loss = (
        float(derivation["modified_duration_years"])
        * (data["yield_change_bp"].to_numpy(dtype=float) / 10000.0)
        * float(derivation["notional_usd"])
    )
    if not np.allclose(implied_loss, data["long_bond_loss_usd"].to_numpy(dtype=float), rtol=1e-10, atol=1e-7):
        raise ValueError("El P&L de entrada no coincide con la regla de duración documentada")
    if str(data["date"].min().date()) != reference["derived_input_period"][0]:
        raise ValueError("La fecha inicial no coincide con el vintage registrado")
    if str(data["date"].max().date()) != reference["derived_input_period"][1]:
        raise ValueError("La fecha final no coincide con el vintage registrado")
    return data.sort_values("date").reset_index(drop=True)


def exact_equal_mass_es(losses: np.ndarray, alpha: float) -> tuple[float, float, float, int, float]:
    """Independent tail integration; return VaR, ES, tail mass, full count, boundary fraction."""
    ordered = np.sort(losses)[::-1]
    tail_equivalents = (1.0 - alpha) * len(ordered)
    full_count = int(math.floor(tail_equivalents))
    fractional = tail_equivalents - full_count
    total = math.fsum(ordered[:full_count].tolist())
    if fractional > 0:
        total += fractional * float(ordered[full_count])
    es = total / tail_equivalents
    ascending = np.sort(losses)
    var_index = min(int(math.ceil(alpha * len(ascending))) - 1, len(ascending) - 1)
    return float(ascending[var_index]), float(es), tail_equivalents / len(ordered), full_count, fractional


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Existing derived Treasury duration P&L proxy CSV")
    args = parser.parse_args()
    input_path = args.input.expanduser().resolve()
    reference = json.loads(REFERENCE_PATH.read_text())
    data = load_proxy(input_path, reference)

    losses = data["long_bond_loss_usd"].to_numpy(dtype=float)
    alpha = float(reference["application"]["alpha"])
    result = weighted_tail(losses, alpha=alpha)
    var_manual, es_manual, tail_probability, whole_scenarios, boundary_fraction = exact_equal_mass_es(losses, alpha)
    if not np.isclose(result.var, var_manual, rtol=0, atol=1e-9):
        raise AssertionError(f"VaR engine/manual mismatch: {result.var} != {var_manual}")
    if not np.isclose(result.es, es_manual, rtol=1e-12, atol=1e-8):
        raise AssertionError(f"ES engine/manual mismatch: {result.es} != {es_manual}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    top = data.assign(loss_rank=losses).sort_values("loss_rank", ascending=False).head(10)
    top_rows = [
        {"date": row.date.strftime("%Y-%m-%d"), "yield_change_bp": float(row.yield_change_bp), "loss_proxy_usd": float(row.long_bond_loss_usd)}
        for row in top.itertuples()
    ]
    summary = {
        "source": reference["source"],
        "series": reference["series"],
        "official_yield_source_files_sha256": reference["official_yield_file_hashes"],
        "derived_input_sha256": sha256_file(input_path),
        "period": [str(data["date"].min().date()), str(data["date"].max().date())],
        "yield_intervals": int(len(data)),
        "duration_years_assumed": reference["derivation"]["modified_duration_years"],
        "notional_usd_assumed": reference["derivation"]["notional_usd"],
        "scenario_probability": "equal per observed consecutive yield-change interval",
        "alpha": alpha,
        "var_loss_proxy_usd": result.var,
        "es_loss_proxy_usd": result.es,
        "tail_probability": tail_probability,
        "tail_equivalent_observations": float((1.0 - alpha) * len(data)),
        "fully_included_worst_observations": whole_scenarios,
        "fraction_of_next_boundary_observation": boundary_fraction,
        "max_observed_loss_proxy_usd": float(np.max(losses)),
        "mean_loss_proxy_usd": float(np.mean(losses)),
        "top_10_loss_proxy_intervals": top_rows,
        "engine_matches_independent_equal_mass_calculation": True,
        "interpretation": "historical expected shortfall over a one-factor, constant-duration P&L proxy; not actual bond or portfolio losses",
        "limitations": [
            "The input is a first-order duration estimate from changes in one 10-year par yield, not marked-to-market instrument P&L.",
            "Assumes modified duration 8 years and USD 10 million notional; neither is an observed holding.",
            "Omits convexity, coupon cash flows, carry, roll-down, curve shape, basis, FX and portfolio diversification.",
            "The 2024-01 to 2026-11 sample omits 2008 and 2020 crisis regimes; empirical tail is uncertain at 714 intervals.",
            "This demonstrates the weighted-ES calculation on an observed-factor proxy and is not a regulatory backtest or production model validation."
        ]
    }
    (OUTPUT / "observed_es_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    pd.DataFrame(
        [
            {"metric": "VaR", "alpha": alpha, "loss_proxy_usd": result.var},
            {"metric": "Expected Shortfall", "alpha": alpha, "loss_proxy_usd": result.es},
        ]
    ).to_csv(OUTPUT / "observed_es_metrics.csv", index=False, float_format="%.8f")

    fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
    ax.hist(losses / 1000.0, bins=35, color="#668da8", edgecolor="white", alpha=0.86)
    ax.axvline(result.var / 1000.0, color="#d28b3c", linewidth=2, linestyle="--", label=f"VaR 97.5% = ${result.var/1000:,.1f}k")
    ax.axvline(result.es / 1000.0, color="#a5483e", linewidth=2, label=f"ES 97.5% = ${result.es/1000:,.1f}k")
    ax.set_title("Proxy de P&L por choque del Treasury a 10 años · D=8 · nocional USD 10m")
    ax.set_xlabel("Pérdida proxy (USD miles; positivo = pérdida) · VaR/ES a 97,5%")
    ax.set_ylabel("Número de intervalos observados")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False)
    fig.savefig(FIGURES / "observed_treasury_es_proxy.png", dpi=180, facecolor="white")
    plt.close(fig)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
