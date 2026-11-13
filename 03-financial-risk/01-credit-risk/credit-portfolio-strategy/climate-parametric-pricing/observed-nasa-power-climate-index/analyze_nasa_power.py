#!/usr/bin/env python3
"""Profile NASA POWER daily precipitation and build a descriptive climate proxy.

Raw source files are read from an external data directory and are not copied.
The companion is a climate-signal exploration, not an insurance validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


CITY_FILES = {
    "Barrancabermeja": "barrancabermeja_daily_2000_2026.csv",
    "Barranquilla": "barranquilla_daily_2000_2026.csv",
    "Bogotá": "bogota_daily_2000_2026.csv",
    "Bucaramanga": "bucaramanga_daily_2000_2026.csv",
    "Cali": "cali_daily_2000_2026.csv",
    "Cartagena": "cartagena_daily_2000_2026.csv",
    "Medellín": "medellin_daily_2000_2026.csv",
    "Neiva": "neiva_daily_2000_2026.csv",
    "Pasto": "pasto_daily_2000_2026.csv",
    "Villavicencio": "villavicencio_daily_2000_2026.csv",
}
PARAMETERS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_city(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, skiprows=15, na_values=[-999])
    frame["date"] = pd.to_datetime(
        frame["YEAR"].astype("Int64").astype(str)
        + frame["DOY"].astype("Int64").astype(str).str.zfill(3),
        format="%Y%j",
        errors="coerce",
    )
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory containing the ten NASA POWER CSVs")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frames: dict[str, pd.DataFrame] = {}
    quality = []
    digests = {}

    for city, filename in CITY_FILES.items():
        path = args.data_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing source file: {path}")
        data = load_city(path)
        frames[city] = data
        expected = pd.date_range(data.date.min(), data.date.max(), freq="D")
        observed_dates = pd.DatetimeIndex(data.date.dropna().unique())
        bad_precip = data.PRECTOTCORR.dropna().lt(0).sum()
        quality.append({
            "city": city,
            "file": filename,
            "sha256": sha256(path),
            "rows_including_header": len(data) + 1,
            "first_date": data.date.min().date().isoformat(),
            "last_date": data.date.max().date().isoformat(),
            "unique_dates": int(data.date.nunique()),
            "duplicate_dates": int(data.date.duplicated().sum()),
            "calendar_dates_missing": int(len(expected.difference(observed_dates))),
            "null_precip_days": int(data.PRECTOTCORR.isna().sum()),
            "negative_precip_values": int(bad_precip),
            "null_by_parameter": {col: int(data[col].isna().sum()) for col in PARAMETERS},
        })
        digests[filename] = quality[-1]["sha256"]

    # Annual comparisons use only complete calendar years; 2026 is partial.
    annual_rows = []
    for city, data in frames.items():
        valid = data.dropna(subset=["date", "PRECTOTCORR"]).copy()
        valid["year"] = valid.date.dt.year
        totals = valid.groupby("year").PRECTOTCORR.agg(total_mm="sum", valid_days="count")
        for year, row in totals.iterrows():
            days = 366 if pd.Timestamp(year=int(year), month=12, day=31).is_leap_year else 365
            annual_rows.append({"city": city, "year": int(year), "precipitation_mm": float(row.total_mm),
                                "valid_days": int(row.valid_days), "expected_days": days,
                                "complete_year": bool(row.valid_days == days)})
    annual = pd.DataFrame(annual_rows)
    annual.to_csv(args.output_dir / "annual_precipitation.csv", index=False, float_format="%.4f")

    complete = annual.query("complete_year and year <= 2025").copy()
    baseline = complete.query("2000 <= year <= 2019").groupby("city").precipitation_mm
    stats = baseline.agg(baseline_mean_mm="mean", baseline_sd_mm="std", p10_mm=lambda s: s.quantile(.10)).reset_index()
    complete = complete.merge(stats, on="city", validate="many_to_one")
    complete["baseline_z"] = (complete.precipitation_mm - complete.baseline_mean_mm) / complete.baseline_sd_mm
    complete["below_baseline_p10"] = complete.precipitation_mm < complete.p10_mm
    complete.to_csv(args.output_dir / "annual_baseline_comparison.csv", index=False, float_format="%.4f")

    recent = complete.query("2020 <= year <= 2025").groupby("city").agg(
        recent_complete_years=("year", "count"), years_below_baseline_p10=("below_baseline_p10", "sum"),
        mean_recent_z=("baseline_z", "mean"), min_recent_z=("baseline_z", "min")
    ).reset_index()
    recent.to_csv(args.output_dir / "recent_descriptive_signal.csv", index=False, float_format="%.4f")

    fig, axes = plt.subplots(2, 5, figsize=(16, 7), sharex=True)
    for ax, (city, subset) in zip(axes.flat, complete.groupby("city", sort=False)):
        ax.plot(subset.year, subset.precipitation_mm, linewidth=1.2, color="#187c80")
        ref = stats.loc[stats.city.eq(city), "baseline_mean_mm"].iloc[0]
        ax.axhline(ref, color="#cf703f", linestyle="--", linewidth=1)
        ax.set_title(city, fontsize=10)
        ax.grid(alpha=.2)
    fig.suptitle("Precipitación anual NASA POWER: diez puntos urbanos de Colombia\nLínea discontinua: media 2000–2019; dato modelado, no pluviómetro", fontsize=13)
    fig.supxlabel("Año (2026 parcial, excluido)")
    fig.supylabel("mm/año")
    fig.tight_layout()
    fig.savefig(args.output_dir / "annual_precipitation_by_city.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    pivot = complete.pivot(index="city", columns="year", values="baseline_z")
    fig, ax = plt.subplots(figsize=(14, 5.5))
    im = ax.imshow(pivot, aspect="auto", cmap="RdYlBu", vmin=-2.5, vmax=2.5)
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_title("Anomalía de precipitación anual frente a climatología urbana 2000–2019")
    fig.colorbar(im, ax=ax, label="desviaciones estándar de la ciudad")
    fig.tight_layout()
    fig.savefig(args.output_dir / "annual_precipitation_anomaly_heatmap.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ordered = recent.sort_values("years_below_baseline_p10")
    ax.barh(ordered.city, ordered.years_below_baseline_p10, color="#187c80")
    ax.axvline(.6, color="#cf703f", linestyle="--", label="0.6 esperado en 6 años si P10 estable")
    ax.set(xlim=(0, 6), xlabel="Años por debajo del P10 propio 2000–2019 (de 6)", title="Años secos recientes: recuento descriptivo 2020–2025")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(args.output_dir / "recent_dry_year_counts.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    manifest = {
        "provider": "NASA POWER",
        "data_type": "gridded/model-derived meteorological estimates; not station observations",
        "source_vintage": "downloaded 2026-07-20; requested through 2026-07-19",
        "parameters": PARAMETERS,
        "cities": list(CITY_FILES),
        "raw_sha256": digests,
        "quality_profile": quality,
        "baseline": "city-specific complete-year precipitation, 2000–2019",
        "recent_window": "2020–2025; complete years only",
        "limits": ["10 urban coordinate points are not department/crop coverage",
                   "annual precipitation alone does not establish insured losses or basis risk",
                   "no pricing, trigger calibration, or causal credit claim is made"],
    }
    (args.output_dir / "source_quality_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"quality": quality, "recent_signal": recent.to_dict(orient="records")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
