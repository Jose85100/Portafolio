#!/usr/bin/env python3
"""Build a quarterly housing starts/completions signal from the DANE CEED annex."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent
PERIODS = pd.period_range("2020Q3", "2026Q2", freq="Q-DEC")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def quarter_rows(ws, start_col: int, end_col: int) -> dict[str, tuple[int, ...]]:
    out = {}
    for row in ws.iter_rows(min_row=15, max_col=end_col, values_only=True):
        year, q = row[start_col], row[start_col + 1]
        if not isinstance(year, int) or q not in {"I", "II", "III", "IV"}:
            continue
        qn = {"I": 1, "II": 2, "III": 3, "IV": 4}[q]
        period = f"{year}Q{qn}"
        if period in out:
            continue
        values = row[start_col + 2:end_col]
        out[period] = tuple(int(v) for v in values if isinstance(v, (int, float)))
    return out


def extract(path: Path) -> pd.DataFrame:
    wb = load_workbook(path, read_only=True, data_only=True)
    if not {"Anexo M", "Anexo O"}.issubset(wb.sheetnames):
        raise ValueError(f"Required CEED sheets missing: {wb.sheetnames}")
    m = quarter_rows(wb["Anexo M"], 1, 10)
    o = quarter_rows(wb["Anexo O"], 1, 11)
    wb.close()
    expected = {str(p) for p in PERIODS}
    if set(m) != expected or set(o) != expected:
        raise ValueError(f"Unexpected quarter coverage: M={len(m)} quarters, O={len(o)} quarters")
    rows = []
    for p in PERIODS:
        key = str(p)
        # Anexo M: starts VIS, No VIS, total; completed VIS, No VIS, total.
        starts_vis, starts_nonvis, starts_total, completed_vis, completed_nonvis, completed_total = m[key][:6]
        # Anexo O: completed apartments/casas/total for VIS, then No VIS, then total housing.
        vis_total, nonvis_total, all_total = o[key][2], o[key][5], o[key][6]
        if (starts_vis + starts_nonvis != starts_total or completed_vis + completed_nonvis != completed_total
                or (completed_vis, completed_nonvis, completed_total) != (vis_total, nonvis_total, all_total)):
            raise ValueError(f"Cross-table reconciliation failed at {key}")
        rows.append({"quarter": key, "starts_vis": starts_vis, "starts_nonvis": starts_nonvis,
                     "starts_total": starts_total, "completed_vis": completed_vis,
                     "completed_nonvis": completed_nonvis, "completed_total": completed_total,
                     "completions_minus_starts": completed_total - starts_total,
                     "completions_to_starts_ratio": completed_total / starts_total})
    df = pd.DataFrame(rows)
    count_columns = ["starts_vis", "starts_nonvis", "starts_total", "completed_vis", "completed_nonvis", "completed_total"]
    if df[count_columns].lt(0).any().any():
        raise ValueError("Negative values in unit counts")
    return df


def build(source: Path, out: Path) -> dict:
    df = extract(source)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "quarterly_housing_starts_completions.csv", index=False, float_format="%.6f")
    periods = pd.PeriodIndex(df.quarter, freq="Q-DEC")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(periods.astype(str), df.starts_total, color="#496d7a", marker="o", linewidth=2, label="Iniciadas")
    ax1.plot(periods.astype(str), df.completed_total, color="#d9822b", marker="o", linewidth=2, label="Culminadas")
    ax1.set(title="Vivienda iniciada y culminada · CEED · 23 áreas de cobertura", ylabel="Unidades en el trimestre")
    ax1.grid(alpha=.25)
    ax1.legend(frameon=False, ncol=2)
    ax2.bar(periods.astype(str), df.completed_vis, color="#496d7a", label="Culminadas VIS")
    ax2.bar(periods.astype(str), df.completed_nonvis, bottom=df.completed_vis, color="#d9822b", label="Culminadas No VIS")
    ax2.set(title="Unidades culminadas por tipo de vivienda", ylabel="Unidades en el trimestre")
    ax2.legend(frameon=False, ncol=2)
    ax2.grid(axis="y", alpha=.25)
    ticks = list(range(0, len(df), 2))
    ax2.set_xticks(ticks, [str(periods[i]) for i in ticks], rotation=45, ha="right")
    fig.text(.01, .005, "Flujos de iniciación y culminación; no representan inventario terminado sin vender ni una cohorte enlazada.", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(out / "ceed_housing_supply_flow.png", dpi=170, facecolor="white")
    plt.close(fig)

    latest = df.iloc[-1]
    prior = df[df.quarter.eq("2025Q2")].iloc[0]
    trailing_current = int(df[df.quarter.isin(["2025Q3", "2025Q4", "2026Q1", "2026Q2"])].completed_total.sum())
    trailing_prior = int(df[df.quarter.isin(["2024Q3", "2024Q4", "2025Q1", "2025Q2"])].completed_total.sum())
    summary = {
        "latest_quarter": "2026Q2", "started": int(latest.starts_total), "completed": int(latest.completed_total),
        "completed_vis": int(latest.completed_vis), "completed_nonvis": int(latest.completed_nonvis),
        "completed_to_starts_ratio": round(float(latest.completions_to_starts_ratio), 6),
        "completed_yoy_change_pct": round((int(latest.completed_total) / int(prior.completed_total) - 1) * 100, 4),
        "trailing_four_quarter_completions": trailing_current,
        "prior_trailing_four_quarter_completions": trailing_prior,
        "trailing_four_quarter_yoy_change_pct": round((trailing_current / trailing_prior - 1) * 100, 4),
    }
    manifest = {
        "provider": "Departamento Administrativo Nacional de Estadística (DANE)",
        "operation": "Censo de Edificaciones (CEED)",
        "source_page": "https://www.dane.gov.co/index.php/estadisticas-por-tema/construccion/censo-de-edificaciones",
        "source_file": "anex-CEED-IItrim2026.xlsx",
        "source_url": "https://www.dane.gov.co/files/operaciones/CEED/anex-CEED-IItrim2026.xlsx",
        "source_sheet_starts_completions": "Anexo M", "source_sheet_crosscheck": "Anexo O",
        "snapshot_date": "2026-11-11", "coverage": "23 areas of coverage; 2020Q3–2026Q2",
        "source_bytes": source.stat().st_size, "source_sha256": sha256(source),
        "quarters": len(df), "source_rows_reconcile_across_annexes": True,
        "required_attribution": "Fuente: Departamento Administrativo Nacional de Estadística (DANE), www.dane.gov.co.",
        "limitations": ["Starts and completions are quarterly flows; their difference is not unsold stock or a measure of absorption.",
                        "The published aggregate workbook does not provide unsold completed units or time-on-market.",
                        "The CEED microdata catalog documents unit sales and sale prices but its microdata file is distributed separately; it is not used in this companion.",
                        "The 23-area coverage is not national coverage; areas and methods may change over time.",
                        "VIS/No VIS series are aggregates and cannot validate project-level demand, pricing, discount policy or losses.",
                        "Workbook-specific redistribution terms are not explicit in the cited release page; source attribution is included and the workbook/microdata are not stored in this repository."]
    }
    (out / "source_quality_manifest.json").write_text(json.dumps({"source": manifest, "summary": summary}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"source": manifest, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="DANE CEED aggregate workbook; keep the source workbook outside this repository")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output_dir)["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
