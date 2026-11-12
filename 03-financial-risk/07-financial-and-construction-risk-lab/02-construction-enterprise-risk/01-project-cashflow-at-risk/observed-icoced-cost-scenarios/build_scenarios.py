#!/usr/bin/env python3
"""Replay a synthetic project cash profile under rolling observed ICOCED paths."""

from __future__ import annotations

import argparse
import hashlib
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


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
REPO_ROOT = HERE.parents[4]
DEFAULT_INPUT = REPO_ROOT / "03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/results/icoced_material_series_bogota.csv"
REFERENCE_PATH = HERE / "data" / "source_reference.json"
CONFIG_PATH = HERE / "scenario_config.json"
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
sys.path.insert(0, str(PROJECT_ROOT))
from src.model import Project  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_index(path: Path, reference: dict) -> pd.DataFrame:
    actual_hash = sha256_file(path)
    expected_hash = reference["reused_derived_input_sha256"]
    if actual_hash != expected_hash:
        raise ValueError(f"SHA-256 del derivado no coincide: {actual_hash} != {expected_hash}")
    data = pd.read_csv(path)
    required = {"period", "geographic_domain", "cost_group", "input", "weight_pct_2021_base", "index_dec_2021_100", "monthly_change_pct"}
    if required - set(data.columns):
        raise ValueError(f"Faltan columnas requeridas: {sorted(required - set(data.columns))}")
    if len(data) != reference["reused_derived_input_rows"]:
        raise ValueError(f"Filas inesperadas: {len(data)}")
    data["period"] = pd.to_datetime(data["period"], errors="coerce")
    if data["period"].isna().any():
        raise ValueError("Hay periodos inválidos")
    data = data.loc[
        data["geographic_domain"].eq(reference["selection"]["geographic_domain"])
        & data["cost_group"].eq(reference["selection"]["cost_group"])
        & data["input"].eq(reference["selection"]["input"])
    ].copy().sort_values("period")
    if len(data) != reference["selection"]["observations"] or data["period"].duplicated().any():
        raise ValueError("Cobertura o unicidad mensual inesperada para la serie ICOCED seleccionada")
    numeric = ["weight_pct_2021_base", "index_dec_2021_100", "monthly_change_pct"]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not np.isfinite(data[column].to_numpy(dtype=float)).all():
            raise ValueError(f"Datos no finitos en {column}")
    if (data["index_dec_2021_100"] <= 0).any():
        raise ValueError("El índice de costos debe ser positivo")
    sel = reference["selection"]
    if str(data["period"].min().strftime("%Y-%m")) != sel["period_start"] or str(data["period"].max().strftime("%Y-%m")) != sel["period_end"]:
        raise ValueError("Rango temporal distinto al snapshot documentado")
    if not np.allclose(data["weight_pct_2021_base"], sel["published_2021_base_weight_pct"], rtol=0, atol=1e-9):
        raise ValueError("El peso publicado del insumo cambió en la serie seleccionada")
    return data.reset_index(drop=True)


def replay(index_path: np.ndarray, config: dict, weight: float) -> dict:
    horizon = int(config["horizon_months"])
    opening = float(config["opening_cash"])
    collections = tuple([float(config["monthly_collections"])] * horizon)
    debt = tuple([float(config["monthly_debt_service"])] * horizon)
    base_costs = tuple([float(config["base_monthly_project_costs"])] * horizon)
    rows = []
    for start in range(len(index_path) - horizon + 1):
        window = index_path[start : start + horizon]
        multiplier = (1.0 - weight) + weight * (window / window[0])
        costs = tuple(float(base_costs[t] * multiplier[t]) for t in range(horizon))
        # Reuse the prototype's data contract for every path, then replay its cash recurrence deterministically.
        project = Project(opening, collections, costs, debt, float(config["liquidity_floor"]))
        cash = project.opening_cash
        peak_shortfall = max(0.0, project.liquidity_floor - cash)
        minimum_cash = cash
        for revenue, cost, debt_service in zip(project.monthly_collections, project.monthly_costs, project.monthly_debt_service, strict=True):
            cash += revenue - cost - debt_service
            if not math.isfinite(cash):
                raise ArithmeticError("Cash accumulation overflow")
            minimum_cash = min(minimum_cash, cash)
            peak_shortfall = max(peak_shortfall, project.liquidity_floor - cash)
        rows.append({
            "scenario_start": start,
            "peak_shortfall_cop_millions": peak_shortfall,
            "minimum_cash_cop_millions": minimum_cash,
            "terminal_cash_cop_millions": cash,
            "index_start": float(window[0]),
            "index_end": float(window[-1]),
            "index_change_pct": float((window[-1] / window[0] - 1.0) * 100),
            "max_concrete_component_multiplier": float(multiplier.max()),
        })
    return {"rows": rows, "baseline_terminal_cash": opening + horizon * (collections[0] - base_costs[0] - debt[0])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Existing derived ICOCED series CSV")
    args = parser.parse_args()
    input_path = args.input.expanduser().resolve()
    reference = json.loads(REFERENCE_PATH.read_text())
    config = json.loads(CONFIG_PATH.read_text())
    data = load_index(input_path, reference)

    idx = data["index_dec_2021_100"].to_numpy(dtype=float)
    weight = float(reference["selection"]["published_2021_base_weight_pct"]) / 100.0
    path_result = replay(idx, config, weight)
    scenarios = pd.DataFrame(path_result["rows"])
    horizon = int(config["horizon_months"])
    expected_scenarios = len(idx) - horizon + 1
    if len(scenarios) != expected_scenarios or expected_scenarios != reference["scenario_application"]["rolling_overlapping_windows"]:
        raise ValueError("Número inesperado de ventanas móviles")

    # Convert scenario start indices to the corresponding official observation dates.
    scenarios["scenario_start_date"] = data.loc[scenarios["scenario_start"], "period"].dt.strftime("%Y-%m").to_numpy()
    scenarios["scenario_end_date"] = data.loc[scenarios["scenario_start"] + horizon - 1, "period"].dt.strftime("%Y-%m").to_numpy()
    scenarios["liquidity_buffer_breach"] = scenarios["peak_shortfall_cop_millions"].gt(0)

    base_cost = float(config["base_monthly_project_costs"])
    no_escalation_cash = float(config["opening_cash"])
    for _ in range(horizon):
        no_escalation_cash += float(config["monthly_collections"]) - base_cost - float(config["monthly_debt_service"])

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    output_columns = [
        "scenario_start_date", "scenario_end_date", "index_start", "index_end", "index_change_pct",
        "max_concrete_component_multiplier", "minimum_cash_cop_millions", "terminal_cash_cop_millions",
        "peak_shortfall_cop_millions", "liquidity_buffer_breach",
    ]
    scenarios[output_columns].to_csv(RESULTS / "historical_index_cash_scenarios.csv", index=False, float_format="%.8f")
    losses = scenarios["peak_shortfall_cop_millions"].to_numpy(dtype=float)
    ordered = np.sort(losses)
    q95 = float(ordered[math.ceil(0.95 * len(ordered)) - 1])
    worst = scenarios.loc[scenarios["peak_shortfall_cop_millions"].idxmax()]
    summary = {
        "source_snapshot_sha256": reference["source_workbook_sha256"],
        "reused_derived_input_sha256": sha256_file(input_path),
        "source_period": [reference["selection"]["period_start"], reference["selection"]["period_end"]],
        "input_series": reference["selection"]["input"],
        "geography": reference["selection"]["geographic_domain"],
        "published_sector_reference_weight_pct": reference["selection"]["published_2021_base_weight_pct"],
        "historical_index_observations": int(len(data)),
        "project_cash_flows": {key: config[key] for key in ["currency", "horizon_months", "opening_cash", "monthly_collections", "base_monthly_project_costs", "monthly_debt_service", "liquidity_floor"]},
        "cash_flows_are_synthetic": True,
        "project_specific_cost_bom_available": False,
        "rolling_overlapping_scenarios": int(len(scenarios)),
        "baseline_no_escalation_terminal_cash_cop_millions": no_escalation_cash,
        "historical_scenario_windows_with_buffer_breach": int(scenarios["liquidity_buffer_breach"].sum()),
        "share_of_overlapping_scenario_windows_with_breach_pct_not_probability": float(scenarios["liquidity_buffer_breach"].mean() * 100),
        "nearest_rank_p95_peak_shortfall_cop_millions_scenario_only": q95,
        "maximum_peak_shortfall_cop_millions_scenario_only": float(worst["peak_shortfall_cop_millions"]),
        "worst_scenario_window": {"start": worst["scenario_start_date"], "end": worst["scenario_end_date"], "index_change_pct": float(worst["index_change_pct"])},
        "method": "24-month rolling ICOCED index paths; concrete component multiplied by its published 2021 sector-basket weight; other costs, collections and debt held flat and synthetic",
        "interpretation": "sector input sensitivity on a synthetic project profile; not observed project cashflow, realized cost overrun, forecast or calibrated CaR",
        "limitations": [
            "ICOCED is a representative sector cost index, not a project invoice, procurement quote or contractual escalator.",
            "The 10.112% published 2021 basket weight is not this synthetic or any real project's bill of quantities.",
            "The 34 rolling windows overlap and do not form independent draws; their fraction is not a probability of breach.",
            "Collections, debt service, non-concrete costs, cash opening and liquidity floor are fixed illustrative assumptions.",
            "No inference is made about any work, developer, lender, contractor or project outcome."
        ]
    }
    (RESULTS / "scenario_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    fig, (ax_index, ax_shortfall) = plt.subplots(1, 2, figsize=(12, 5.5), constrained_layout=True)
    dates = data["period"]
    ax_index.plot(dates, idx, color="#2c6d8d", linewidth=2)
    ax_index.set_title("ICOCED · concreto común")
    ax_index.set_ylabel("Índice de costo · base dic-2021 = 100")
    ax_index.set_xlabel("Mes · Bogotá y Cundinamarca")
    ax_index.xaxis.set_major_locator(mdates.YearLocator())
    ax_index.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_index.grid(alpha=0.2)

    ordered_scenarios = scenarios.sort_values("peak_shortfall_cop_millions", ascending=False).reset_index(drop=True)
    y = np.arange(len(ordered_scenarios))
    colors = np.where(ordered_scenarios["liquidity_buffer_breach"], "#c65f34", "#5b9b7b")
    ax_shortfall.barh(y, ordered_scenarios["peak_shortfall_cop_millions"], color=colors)
    ax_shortfall.invert_yaxis()
    ax_shortfall.set_title("Faltante máximo por ventana (flujo sintético)")
    ax_shortfall.set_xlabel("Millones COP · no es pérdida observada")
    ax_shortfall.set_ylabel("Ventanas móviles de 24 meses")
    ax_shortfall.grid(axis="x", alpha=0.2)
    fig.suptitle("Escenario sectorial ICOCED sobre flujo de caja sintético", fontsize=14)
    fig.savefig(FIGURES / "icoced_cashflow_scenarios.png", dpi=180, facecolor="white")
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
