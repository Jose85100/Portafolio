"""Descriptive temporal distribution comparison for DANE monthly CPI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data" / "dane-ipc-indices-oct2026.xlsx"
OUT = ROOT / "reports"
EXPECTED_SOURCE_SHA256 = "4e8366bf2d03d4bdc15d14b1b21b12a6eec6c3695926abd503a430858ef74e2e"
MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_national_index(path: Path) -> pd.Series:
    raw = pd.read_excel(path, sheet_name="IndicesIPC", header=None)
    header = next(i for i, row in raw.iterrows() if str(row.iloc[0]).strip() == "Mes")
    data = raw.iloc[header + 1 :].copy()
    data = data[data.iloc[:, 0].astype(str).str.strip().isin(MONTHS)]
    records = []
    month_number = {month: i for i, month in enumerate(MONTHS, start=1)}
    for _, row in data.iterrows():
        month = str(row.iloc[0]).strip()
        for col in range(1, len(row)):
            year = pd.to_numeric(raw.iloc[header, col], errors="coerce")
            value = pd.to_numeric(row.iloc[col], errors="coerce")
            if pd.notna(year) and pd.notna(value):
                records.append((pd.Period(year=int(year), month=month_number[month], freq="M"), float(value)))
    series = pd.Series(dict(records), dtype=float).sort_index()
    expected = pd.period_range(series.index.min(), series.index.max(), freq="M")
    if series.index.has_duplicates or not series.index.equals(expected) or (series <= 0).any():
        raise ValueError("El índice debe ser positivo, único y continuo por mes")
    return series


def psi_from_reference_bins(reference: np.ndarray, current: np.ndarray, bins: int = 10, pseudocount: float = 0.5) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    # Fixed reference deciles. Repeated values can collapse adjacent quantiles;
    # unique cut points preserve valid bins for the rounded official index.
    finite_edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(finite_edges) < 3:
        raise ValueError("Muy pocos valores de referencia distintos para calcular PSI")
    edges = np.r_[-np.inf, finite_edges[1:-1], np.inf]
    ref_counts = np.histogram(reference, bins=edges)[0].astype(float)
    cur_counts = np.histogram(current, bins=edges)[0].astype(float)
    ref_share = (ref_counts + pseudocount) / (len(reference) + pseudocount * len(ref_counts))
    cur_share = (cur_counts + pseudocount) / (len(current) + pseudocount * len(cur_counts))
    psi = float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))
    return psi, edges, ref_share, cur_share


def main() -> None:
    OUT.mkdir(exist_ok=True)
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"Hash del snapshot inesperado: {source_hash}")
    index = read_national_index(SOURCE)
    monthly_inflation = (index.pct_change() * 100).dropna()
    monthly_inflation.index = monthly_inflation.index.astype(str)
    monthly_inflation.rename("inflacion_mensual_pct").to_csv(OUT / "observed_monthly_inflation.csv", index_label="month")
    reference = monthly_inflation.loc["2010-01":"2019-12"].to_numpy()
    current = monthly_inflation.loc["2020-01":"2026-10"].to_numpy()
    if len(reference) != 120 or len(current) != 82:
        raise ValueError(f"Ventanas incompletas: referencia={len(reference)}, comparación={len(current)}")
    psi, edges, ref_share, cur_share = psi_from_reference_bins(reference, current)
    ks_d = float(ks_2samp(reference, current, method="auto").statistic)
    # PSI cutoffs are commonly used monitoring heuristics; here they do not
    # represent calibrated institutional limits or a model-performance alert.
    heuristic_band = "bajo (<0.10)" if psi < .10 else "intermedio (0.10–0.25)" if psi < .25 else "alto (>=0.25)"
    result = {
        "edition": "DANE CPI temporal distribution comparison",
        "source": "DANE, IPC total nacional, Índices, serie de empalme; base diciembre 2018 = 100",
        "source_url": "https://www.dane.gov.co/files/operaciones/IPC/oct2026/anex-IPC-Indices-oct2026.xlsx",
        "publication_date": "2026-11-09",
        "source_snapshot": SOURCE.name,
        "source_sha256": source_hash,
        "derived_csv_sha256": sha256(OUT / "observed_monthly_inflation.csv"),
        "source_index_period": [str(index.index.min()), str(index.index.max())],
        "proxy_definition": "Cambio mensual porcentual del índice nacional total: 100 * (IPC_t / IPC_(t-1) - 1).",
        "reference_window": ["2010-01", "2019-12"],
        "comparison_window": ["2020-01", "2026-10"],
        "reference_n_months": int(len(reference)),
        "comparison_n_months": int(len(current)),
        "reference_mean_pct": float(np.mean(reference)),
        "comparison_mean_pct": float(np.mean(current)),
        "reference_median_pct": float(np.median(reference)),
        "comparison_median_pct": float(np.median(current)),
        "psi": psi,
        "psi_heuristic_band": heuristic_band,
        "psi_method": {"bins": "deciles of reference window; unique cutpoints after ties", "n_bins": int(len(edges) - 1), "pseudocount_per_bin": 0.5, "thresholds": {"0.10": "heuristic indication", "0.25": "heuristic large shift"}},
        "ks_statistic_d": ks_d,
        "ks_p_value": None,
        "ks_reason_no_p_value": "Monthly observations are serially dependent; the iid two-sample KS p-value is not used for inference.",
        "interpretation": "Descriptive change in one national time series' distribution between fixed periods; not model drift or predictive degradation.",
        "limitations": [
            "Windows differ in duration (120 vs 82 months) and macroeconomic regimes; the contrast does not attribute causes.",
            "Inflation is a derived proxy from a rounded, revised official index; measurement and methodological revisions may affect values.",
            "PSI bin cutoffs and smoothing are heuristics, sensitive to binning and window choice; they are not calibrated alerts.",
            "KS D is descriptive here; serial dependence invalidates iid p-value interpretation, so no p-value is reported.",
            "This does not measure model performance, population stability of customers, or suitability for operational monitoring."
        ]
    }
    (OUT / "official_distribution_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    positions = np.arange(len(ref_share))
    width = .38
    axes[0].bar(positions - width / 2, ref_share, width, label="2010–2019", color="#4676a9")
    axes[0].bar(positions + width / 2, cur_share, width, label="2020–oct 2026", color="#d17c34")
    axes[0].set(title=f"PSI = {psi:.3f} · banda heurística {heuristic_band}", xlabel="Decil de referencia", ylabel="Proporción por bin")
    axes[0].set_xticks(positions, [str(i + 1) for i in positions])
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=.2)
    for values, label, color in [(reference, "2010–2019", "#4676a9"), (current, "2020–oct 2026", "#d17c34")]:
        sorted_values = np.sort(values)
        axes[1].step(sorted_values, np.arange(1, len(sorted_values) + 1) / len(sorted_values), where="post", label=label, color=color)
    axes[1].set(title=f"KS D = {ks_d:.3f} · sin p-valor iid", xlabel="Inflación mensual (%)", ylabel="Distribución acumulada")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=.2)
    fig.suptitle("IPC Colombia: comparación descriptiva de distribuciones")
    fig.tight_layout()
    fig.savefig(OUT / "official_distribution.png", dpi=170)
    plt.close(fig)
    print(f"DANE snapshot SHA-256: {source_hash}")
    print(f"Inflación mensual observada: n={len(reference)} vs n={len(current)}")
    print(f"Media: {np.mean(reference):.4f}% vs {np.mean(current):.4f}% | mediana: {np.median(reference):.4f}% vs {np.median(current):.4f}%")
    print(f"PSI={psi:.4f} ({heuristic_band}, heurístico) | KS D={ks_d:.4f}; p-value no reportado por dependencia temporal")


if __name__ == "__main__":
    main()
