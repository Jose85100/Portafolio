"""Observed-data portfolio review triage for public ICETEX aggregates."""
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
DATA = ROOT / "data"
OUT = ROOT / "reports"
RAW = DATA / "icetex-dugh-vkir-2026-11-10.json"
TABLE = DATA / "icetex-delinquency-observed.csv"
SOURCE_MANIFEST = DATA / "source-manifest.json"
EXPECTED_RAW_SHA256 = "b91afdd83dd9738fb0dcd9606f67ecbdff2fd0da2af31138d9aeb68f83867a7e"
EXPECTED_TABLE_SHA256 = "c856d4e8ac26b63347d18e722f5467a7f9421dce9b01ab79d3aad4ca5f13ffcf"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    raw_hash = file_hash(RAW)
    table_hash = file_hash(TABLE)
    if raw_hash != EXPECTED_RAW_SHA256 or table_hash != EXPECTED_TABLE_SHA256:
        raise ValueError("El snapshot de ICETEX no coincide con los hashes fijados")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    if manifest["source_snapshot_sha256"] != raw_hash or manifest["sha256"] != table_hash:
        raise ValueError("El manifest de procedencia no concilia con los archivos")

    data = pd.read_csv(TABLE, parse_dates=["fecha_corte"])
    required = {"fecha_corte", "departamento", "epoca_cartera", "creditos_total", "creditos_mora_mayor_90d", "proporcion_mora_mayor_90d"}
    if not required.issubset(data.columns):
        raise ValueError("Faltan campos de steering requeridos")
    if data.duplicated(["fecha_corte", "departamento", "epoca_cartera"]).any():
        raise ValueError("Hay filas duplicadas al grano fecha-departamento-fase")
    if (data["creditos_total"] <= 0).any() or (data["creditos_mora_mayor_90d"] > data["creditos_total"]).any():
        raise ValueError("Conteos incompatibles con el grano agregado")
    dates = sorted(data.fecha_corte.unique())
    latest = pd.Timestamp(dates[-1])
    cut = data[data.fecha_corte.eq(latest)].copy()
    if latest.strftime("%Y-%m-%d") != "2026-09-30" or len(cut) != 68 or cut.departamento.nunique() != 34:
        raise ValueError("El corte final no es el panel completo esperado (34 departamentos × 2 fases)")

    cut["prevalencia_mora_90d"] = cut.creditos_mora_mayor_90d / cut.creditos_total
    baseline = (cut.groupby("epoca_cartera").creditos_mora_mayor_90d.sum()
                / cut.groupby("epoca_cartera").creditos_total.sum()).to_dict()
    cut["baseline_fase"] = cut.epoca_cartera.map(baseline)
    cut["exceso_vs_baseline_pp"] = (cut.prevalencia_mora_90d - cut.baseline_fase) * 100
    cut = cut.sort_values(["epoca_cartera", "creditos_mora_mayor_90d"], ascending=[True, False])
    cut["ranking_carga_fase"] = cut.groupby("epoca_cartera").creditos_mora_mayor_90d.rank(method="first", ascending=False).astype(int)
    cut.to_csv(OUT / "latest_cut_ranked.csv", index=False)

    top_workload = {}
    high_rate = {}
    threshold_sensitivity = {}
    for phase, group in cut.groupby("epoca_cartera", sort=True):
        top_workload[phase] = group.nlargest(5, "creditos_mora_mayor_90d")[
            ["departamento", "creditos_total", "creditos_mora_mayor_90d", "prevalencia_mora_90d", "exceso_vs_baseline_pp"]
        ].to_dict("records")
        high_rate[phase] = group[(group.creditos_total >= 500) & (group.exceso_vs_baseline_pp > 0)].nlargest(
            5, "prevalencia_mora_90d"
        )[["departamento", "creditos_total", "creditos_mora_mayor_90d", "prevalencia_mora_90d", "exceso_vs_baseline_pp"]].to_dict("records")
        threshold_sensitivity[phase] = {}
        base_names = [x["departamento"] for x in top_workload[phase]]
        for minimum in [0, 100, 500, 1000]:
            names = group[group.creditos_total >= minimum].nlargest(5, "creditos_mora_mayor_90d").departamento.tolist()
            threshold_sensitivity[phase][str(minimum)] = {"top5": names, "same_as_unfiltered": names == base_names}

    trend = (data.groupby(["fecha_corte", "epoca_cartera"], as_index=False)
             .agg(creditos_mora_mayor_90d=("creditos_mora_mayor_90d", "sum"), creditos_total=("creditos_total", "sum")))
    trend["prevalencia_mora_90d"] = trend.creditos_mora_mayor_90d / trend.creditos_total
    trend.to_csv(OUT / "portfolio_phase_trend.csv", index=False)
    results = {
        "decision_question": "Which department × portfolio-phase cohorts should be reviewed first by a human collections/portfolio committee?",
        "admissible_decision": "Use observed overdue case volume as a workload queue, then review prevalence relative to phase aggregate as a separate severity signal; no automatic limit, originations, or policy changes.",
        "source": "ICETEX, Comportamiento de Cartera y Crédito (datos.gov.co dataset dugh-vkir)",
        "source_url": manifest["source_url"],
        "source_last_updated": manifest["source_last_updated"],
        "snapshot_as_of": manifest["as_of"],
        "source_raw_sha256": raw_hash,
        "validated_table_sha256": table_hash,
        "grain": manifest["grain"],
        "quality_scope": {"source_rows": manifest["source_rows"], "validated_rows": manifest["validated_rows"],
                          "rejected_rows": manifest["rejected_rows"], "rejected_cut": manifest["rejected_cuts"],
                          "complete_dates": len(dates), "departments_per_cut": 34, "latest_complete_cut": latest.strftime("%Y-%m-%d")},
        "proxy_definition": "Prevalencia observada = créditos con mora >90 días / créditos totales por departamento × fase; carga observada = conteo absoluto de créditos con mora >90 días.",
        "latest_phase_baseline": {phase: float(value) for phase, value in baseline.items()},
        "top5_workload_by_phase": top_workload,
        "high_rate_review_candidates_by_phase": high_rate,
        "denominator_sensitivity_minimum_total_credits": threshold_sensitivity,
        "tradeoff": "Absolute cases prioritize review workload and favor large segments; rate above a phase baseline highlights relative severity and can elevate smaller segments. Keep both views rather than compressing them into an unvalidated score.",
        "limitations": [
            "ICETEX student lending is not MCA, digital lending, or the Colombian banking system; results are an external public proxy, not validation of those portfolios.",
            "Aggregate stock prevalence is not borrower PD, a transition probability, LGD, causal treatment effect, or collection effectiveness.",
            "Counts do not include exposure balance or loss severity, and department is residence geography rather than lender controllable risk segment.",
            "The 2025-06-30 cut is omitted because source counts failed reconciliation; the 18 remaining cuts are complete but not publication-vintage backtests.",
            "Top-five and denominator sensitivity are triage aids; confirm data quality, business capacity, representative cohorts, and operational causes before action."
        ]
    }
    (OUT / "official_steering_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")

    colors = {"AMORTIZACION": "#b45309", "ESTUDIOS": "#2563eb"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    for phase, group in trend.groupby("epoca_cartera"):
        axes[0].plot(group.fecha_corte, group.prevalencia_mora_90d * 100, marker="o", ms=3,
                     color=colors.get(phase), label=phase.title())
    axes[0].axvline(pd.Timestamp("2025-06-30"), color="#6b7280", ls=":", lw=1)
    axes[0].annotate("corte excluido\n(no concilia)", (pd.Timestamp("2025-06-30"), axes[0].get_ylim()[1] * .85),
                     xytext=(5, 0), textcoords="offset points", fontsize=8, color="#4b5563")
    axes[0].set(title="Cartera vencida >90 días, agregado ICETEX", ylabel="Créditos >90 días / total (%)", xlabel="Fecha de corte")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=.2)
    for phase, group in cut.groupby("epoca_cartera"):
        sizes = 25 + 140 * np.sqrt(group.creditos_mora_mayor_90d / max(cut.creditos_mora_mayor_90d.max(), 1))
        axes[1].scatter(group.creditos_total, group.prevalencia_mora_90d * 100, s=sizes,
                        alpha=.72, color=colors.get(phase), label=phase.title(), edgecolor="white", linewidth=.35)
        axes[1].axhline(baseline[phase] * 100, color=colors.get(phase), ls="--", lw=1, alpha=.65)
        for row in group.nlargest(3, "creditos_mora_mayor_90d").itertuples():
            axes[1].annotate(row.departamento.title(), (row.creditos_total, row.prevalencia_mora_90d * 100),
                             xytext=(4, 3), textcoords="offset points", fontsize=7)
    axes[1].set_xscale("log")
    axes[1].set(title="Corte 2026-09: volumen frente a prevalencia", xlabel="Créditos en el segmento (escala log)", ylabel="Mora >90 días (%)")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=.2)
    fig.suptitle("ICETEX observado · apoyo para priorizar revisión humana, no una regla de originación")
    fig.tight_layout()
    fig.savefig(OUT / "official_steering_dashboard.png", dpi=170)
    plt.close(fig)

    print(f"ICETEX snapshot SHA-256: {raw_hash}")
    print(f"Valid rows={len(data)} | dates={len(dates)} | latest complete cut={latest.date()} | groups={len(cut)}")
    for phase, items in top_workload.items():
        print(f"{phase} phase baseline={baseline[phase]:.4%}; workload top5:")
        for item in items:
            print(f"  {item['departamento']}: >90d={item['creditos_mora_mayor_90d']:,}/{item['creditos_total']:,} ({item['prevalencia_mora_90d']:.2%})")


if __name__ == "__main__":
    main()
