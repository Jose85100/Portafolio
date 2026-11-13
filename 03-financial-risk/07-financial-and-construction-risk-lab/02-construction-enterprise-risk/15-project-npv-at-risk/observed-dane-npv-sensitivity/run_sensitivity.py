#!/usr/bin/env python3
"""Apply observed DANE price changes to an explicitly hypothetical project NPV."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
IPVN = LAB / "02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes/ipvn_quarterly_derived.csv"
ICOCED = LAB / "02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/results/icoced_material_series_bogota.csv"
EXPECTED = {
    "ipvn": "5bcc2c7cce6a1f51a4a05069497a75ab794937fa9ac5922b22da4f081574cb8c",
    "icoced": "b2e0b7bb52b8b7b588bc7c0bafefc4e54510906694da34a35b3c692de85a4daa",
}
HORIZON_Q = 8
DISCOUNT_EA = 0.12
NONMATERIAL_COST_Q_COP_BN = 2.0
CONCRETE_COST_Q_COP_BN = 3.0
SALE_PROCEEDS_BASE_COP_BN = 45.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_inputs() -> tuple[dict[str, float], dict[str, float], dict[str, str]]:
    hashes = {"ipvn": sha256(IPVN), "icoced": sha256(ICOCED)}
    for name, actual in hashes.items():
        if actual != EXPECTED[name]:
            raise ValueError(f"{name} derived input SHA-256 mismatch: {actual}")
    ipvn: dict[str, float] = {}
    with IPVN.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ipvn[row["period"]] = float(row["quarterly_change_total_pct"])

    monthly: dict[str, list[float]] = {}
    with ICOCED.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["input"] != "Concreto común" or row["geographic_domain"] != "Bogotá_Cundinamarca AR":
                continue
            period = row["period"]
            year, month = int(period[:4]), int(period[5:7])
            quarter = (month - 1) // 3 + 1
            key = f"{year}Q{quarter}"
            monthly.setdefault(key, []).append(float(row["index_dec_2021_100"]))
    concrete = {q: sum(values) / len(values) for q, values in monthly.items() if len(values) == 3}
    if len(ipvn) < HORIZON_Q or len(concrete) < HORIZON_Q:
        raise ValueError("Insufficient quarterly source coverage")
    return ipvn, concrete, hashes


def npv_for_window(periods: list[str], ipvn: dict[str, float], concrete: dict[str, float], annual_discount: float) -> dict[str, float]:
    first_concrete = concrete[periods[0]]
    cumulative_revenue_factor = 1.0
    pv_costs = 0.0
    for q, period in enumerate(periods, start=1):
        cumulative_revenue_factor *= 1.0 + ipvn[period] / 100.0
        concrete_factor = concrete[period] / first_concrete
        quarter_cost = NONMATERIAL_COST_Q_COP_BN + CONCRETE_COST_Q_COP_BN * concrete_factor
        pv_costs += quarter_cost / ((1.0 + annual_discount) ** (q / 4.0))
    revenue_nominal = SALE_PROCEEDS_BASE_COP_BN * cumulative_revenue_factor
    pv_revenue = revenue_nominal / ((1.0 + annual_discount) ** (HORIZON_Q / 4.0))
    return {
        "revenue_price_change_pct": (cumulative_revenue_factor - 1.0) * 100.0,
        "concrete_index_change_pct": (concrete[periods[-1]] / first_concrete - 1.0) * 100.0,
        "nominal_sale_proceeds_cop_bn": revenue_nominal,
        "pv_costs_cop_bn": pv_costs,
        "pv_sale_proceeds_cop_bn": pv_revenue,
        "npv_cop_bn": pv_revenue - pv_costs,
    }


def main() -> None:
    ipvn, concrete, hashes = load_inputs()
    common = sorted(set(ipvn) & set(concrete))
    windows = []
    for i in range(len(common) - HORIZON_Q + 1):
        periods = common[i:i + HORIZON_Q]
        if len(periods) == HORIZON_Q and all(
            (int(periods[j + 1][:4]) * 4 + int(periods[j + 1][-1]))
            - (int(periods[j][:4]) * 4 + int(periods[j][-1])) == 1
            for j in range(HORIZON_Q - 1)
        ):
            windows.append({"window_start": periods[0], "window_end": periods[-1], **npv_for_window(periods, ipvn, concrete, DISCOUNT_EA)})
    if not windows:
        raise ValueError("No contiguous historical 8-quarter windows")
    base_cost_pv = sum((NONMATERIAL_COST_Q_COP_BN + CONCRETE_COST_Q_COP_BN) / ((1 + DISCOUNT_EA) ** (q / 4)) for q in range(1, HORIZON_Q + 1))
    base_revenue_pv = SALE_PROCEEDS_BASE_COP_BN / ((1 + DISCOUNT_EA) ** (HORIZON_Q / 4))
    base_npv = base_revenue_pv - base_cost_pv
    sorted_npv = sorted(x["npv_cop_bn"] for x in windows)
    median_npv = sorted_npv[len(sorted_npv) // 2]
    worst = min(windows, key=lambda x: x["npv_cop_bn"])
    best = max(windows, key=lambda x: x["npv_cop_bn"])
    selected = [worst, sorted(windows, key=lambda x: x["npv_cop_bn"])[len(windows) // 2], best]
    discount_sensitivity = []
    for scenario in selected:
        periods = [p for p in common if scenario["window_start"] <= p <= scenario["window_end"]]
        for rate in (0.10, 0.12, 0.14):
            discount_sensitivity.append({"scenario": f"{scenario['window_start']}–{scenario['window_end']}", "discount_rate_ea_pct": rate * 100, **npv_for_window(periods, ipvn, concrete, rate)})

    out = ROOT / "results"
    figs = ROOT / "figures"
    out.mkdir(exist_ok=True)
    figs.mkdir(exist_ok=True)
    with (out / "historical_window_npvs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(windows[0]))
        writer.writeheader(); writer.writerows(windows)
    with (out / "discount_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(discount_sensitivity[0]))
        writer.writeheader(); writer.writerows(discount_sensitivity)

    fig, ax = plt.subplots(figsize=(10, 5.2))
    xs = list(range(len(windows)))
    ys = [x["npv_cop_bn"] for x in windows]
    ax.bar(xs, ys, color=["#b84a4a" if y < base_npv else "#347c91" for y in ys])
    ax.axhline(base_npv, color="#222222", linestyle="--", label=f"Base hipotético sin shocks: COP {base_npv:.2f} mil millones")
    ax.set_xticks(xs, [x["window_start"] for x in windows], rotation=45, ha="right")
    ax.set_xlabel("Inicio de ventana (cada ventana abarca 8 trimestres)")
    ax.set_ylabel("NPV ilustrativo (COP miles de millones)")
    ax.set_title("Ventanas históricas de 8 trimestres: sensibilidad a IPVN y concreto")
    ax.grid(axis="y", alpha=.22); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(figs / "historical_window_npv.png", dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.scatter([x["concrete_index_change_pct"] for x in windows], [x["revenue_price_change_pct"] for x in windows], color="#347c91")
    for row in (worst, best):
        ax.annotate(f"{row['window_start']}–{row['window_end']}", (row["concrete_index_change_pct"], row["revenue_price_change_pct"]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Cambio observado índice DANE de concreto (%)")
    ax.set_ylabel("Cambio acumulado observado IPVN total (%)")
    ax.set_title("Factores observados por ventana (no son una distribución conjunta de pérdidas)")
    ax.grid(alpha=.22); fig.tight_layout(); fig.savefig(figs / "observed_factor_windows.png", dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for label, rows in _group_by(discount_sensitivity, "scenario").items():
        ax.plot([r["discount_rate_ea_pct"] for r in rows], [r["npv_cop_bn"] for r in rows], marker="o", label=label)
    ax.set_xlabel("Tasa de descuento hipotética efectiva anual (%)")
    ax.set_ylabel("NPV ilustrativo (COP miles de millones)")
    ax.set_title("Sensibilidad de descuento en ventanas históricas seleccionadas")
    ax.grid(alpha=.22); ax.legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(figs / "discount_rate_sensitivity.png", dpi=170); plt.close(fig)

    ipvn_summary = json.loads((LAB / "02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes/summary.json").read_text())
    icoced_manifest = json.loads((LAB / "02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/results/manifest.json").read_text())
    summary = {
        "purpose": "Descriptive historical-factor sensitivity for a hypothetical project; not a forecast, loss distribution, or project validation.",
        "historical_windows": len(windows), "window_horizon_quarters": HORIZON_Q,
        "window_coverage": [windows[0]["window_start"], windows[-1]["window_end"]],
        "latest_observed_window": {k: round(v, 4) if isinstance(v, float) else v for k, v in windows[-1].items()},
        "illustrative_project_assumptions": {
            "base_sale_proceeds_at_quarter_8_cop_bn": SALE_PROCEEDS_BASE_COP_BN,
            "nonmaterial_cost_per_quarter_cop_bn": NONMATERIAL_COST_Q_COP_BN,
            "concrete_cost_tranche_per_quarter_cop_bn": CONCRETE_COST_Q_COP_BN,
            "discount_rate_effective_annual": DISCOUNT_EA,
            "discount_rate_is_assumption_not_observed_wacc": True,
        },
        "base_npv_no_price_shocks_cop_bn": round(base_npv, 6),
        "historical_window_npv_min_median_max_cop_bn": [round(sorted_npv[0], 6), round(median_npv, 6), round(sorted_npv[-1], 6)],
        "lowest_modeled_npv_window": {k: round(v, 4) if isinstance(v, float) else v for k, v in worst.items()},
        "highest_modeled_npv_window": {k: round(v, 4) if isinstance(v, float) else v for k, v in best.items()},
        "input_sha256": hashes,
        "upstream_source_sha256": {"dane_icoced_xlsx": icoced_manifest["sha256"], "dane_ipvn_xlsx": ipvn_summary["source_sha256"]},
        "quality": {"common_complete_quarters": common, "observed_windows_are_overlapping_descriptive_scenarios": True, "probability_or_var_estimated": False},
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = [out / "historical_window_npvs.csv", out / "discount_sensitivity.csv", out / "summary.json",
               figs / "historical_window_npv.png", figs / "observed_factor_windows.png", figs / "discount_rate_sensitivity.png"]
    manifest = {
        "method": "rolling, overlapping 8-quarter historical changes applied to a fixed hypothetical cash-flow schedule",
        "source_inputs_sha256": hashes,
        "upstream_raw_source_sha256": summary["upstream_source_sha256"],
        "script_sha256": sha256(Path(__file__).resolve()),
        "output_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in outputs},
        "qa": {"input_hashes_match": True, "complete_aligned_windows": len(windows),
               "window_horizon_quarters": HORIZON_Q, "no_probability_or_var_estimated": True},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def _group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(str(row[key]), []).append(row)
    return out


if __name__ == "__main__":
    main()
