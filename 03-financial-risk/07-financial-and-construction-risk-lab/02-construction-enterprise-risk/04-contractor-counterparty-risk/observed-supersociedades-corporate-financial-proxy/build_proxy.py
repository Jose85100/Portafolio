#!/usr/bin/env python3
"""Build an anonymous sector-level financial profile from Supersociedades' top-10k data."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
FIELDS = ["a_o_de_corte", "macrosector", "ingresos_operacionales", "ganancia_p_rdida",
          "total_activos", "total_pasivos", "total_patrimonio"]


def amount(value: object) -> float:
    """Parse the source's USD-style display of COP billions, preserving negatives."""
    s = str(value).strip().replace("$", "").replace(",", "").replace(" ", "")
    if s.startswith("-"):
        return -float(s[1:])
    return float(s)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(source: Path, out: Path) -> dict:
    records = json.loads(source.read_text(encoding="utf-8"))
    df = pd.DataFrame(records)
    if len(df) != 50_000 or set(FIELDS) - set(df.columns):
        raise ValueError(f"Unexpected source shape/fields: rows={len(df)}, cols={list(df.columns)}")
    df = df[FIELDS].copy()
    df["year"] = pd.to_numeric(df.pop("a_o_de_corte"), errors="coerce").astype("Int64")
    df = df.rename(columns={"macrosector": "sector"})
    for col in FIELDS[2:]:
        df[col] = df[col].map(amount)
    if df.isna().any().any() or not set(df.year.astype(int).unique()) == {2021, 2022, 2023, 2024, 2025}:
        raise ValueError("Missing/non-numeric values or unexpected years")
    df["liabilities_assets"] = df.total_pasivos / df.total_activos.where(df.total_activos > 0)
    df["profit_margin"] = df.ganancia_p_rdida / df.ingresos_operacionales.where(df.ingresos_operacionales > 0)
    df["loss_reported"] = df.ganancia_p_rdida < 0
    summary = df.groupby(["year", "sector"], as_index=False).agg(
        companies=("sector", "size"),
        companies_with_positive_assets=("liabilities_assets", "count"),
        companies_with_positive_revenue=("profit_margin", "count"),
        aggregate_assets_cop_bn=("total_activos", "sum"),
        aggregate_liabilities_cop_bn=("total_pasivos", "sum"),
        weighted_liabilities_assets=("liabilities_assets", "mean"),
        median_company_liabilities_assets=("liabilities_assets", "median"),
        share_reporting_loss=("loss_reported", "mean"),
        median_profit_margin=("profit_margin", "median"),
    )
    # Weighted leverage is the ratio of sector totals; do not average firm ratios for this measure.
    # For the ratio of sums, exclude non-positive asset rows and disclose the valid denominator count.
    positive_assets = df.loc[df.total_activos > 0].groupby(["year", "sector"], as_index=False).agg(
        valid_assets=("total_activos", "sum"), valid_liabilities=("total_pasivos", "sum"))
    summary = summary.merge(positive_assets, on=["year", "sector"], how="left")
    summary["weighted_liabilities_assets"] = summary.valid_liabilities / summary.valid_assets
    out.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out / "sector_financial_profile.csv", index=False, float_format="%.6f")
    years = sorted(summary.year.unique())
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for sector, group in summary.groupby("sector"):
        group = group.sort_values("year")
        ax.plot(group.year, group.weighted_liabilities_assets, marker="o", linewidth=1.8, label=sector)
    ax.set(title="Pasivos / activos agregados por macrosector · 10.000 empresas", xlabel="Año de corte", ylabel="Razón pasivos / activos")
    ax.set_xticks(years)
    ax.grid(alpha=.25)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.text(.01, .005, "Muestra anual de las 10.000 empresas más grandes; no representa todas las empresas ni predice default.", fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, 1))
    fig.savefig(out / "sector_leverage_profile.png", dpi=170, facecolor="white")
    plt.close(fig)
    manifest = {
        "provider": "Superintendencia de Sociedades de Colombia",
        "dataset": "10.000 Empresas mas Grandes del País", "dataset_id": "6cat-2gcs",
        "dataset_page": "https://www.datos.gov.co/Comercio-Industria-y-Turismo/10-000-Empresas-mas-Grandes-del-Pa-s/6cat-2gcs",
        "source_csv_api": "https://www.datos.gov.co/resource/6cat-2gcs.json",
        "snapshot_date": "2026-11-11", "years": [2021, 2022, 2023, 2024, 2025],
        "rows": len(df), "source_fields": FIELDS, "source_sha256": sha256(source), "source_bytes": source.stat().st_size,
        "output_contains_company_identifiers": False,
        "units": "Billones de COP, as displayed by source; rounded source values",
        "limitations": ["Annual top-10,000-company rankings are selected samples, not a stable panel or census; entrants/exits can drive changes.",
                        "Aggregate accounting ratios are not default, PD, LGD, liquidity, or credit quality measures.",
                        "The source displays values rounded to two decimals in COP billions; firm-level ratios near zero equity can be unstable.",
                        "Rows with non-positive assets or revenue are excluded from their respective ratio denominator; counts are disclosed.",
                        "No construction-company-only classification, contractor matching, outcome, or project linkage is asserted.",
                        "Source metadata identifies Supersociedades as owner; license/reuse terms are not explicit in the catalog."]
    }
    (out / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="API JSON snapshot outside Git; select only the seven documented fields")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    result = build(args.input, args.output_dir)
    print(json.dumps({"rows": result["rows"], "years": result["years"], "sha256": result["source_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
