"""Reproduce the official public-data evidence case, not an ECL estimate."""
import argparse
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SOURCE_DIR = ROOT / "03-financial-risk/01-credit-risk/observed-data-proxies"
sys.path.insert(0, str(SOURCE_DIR / "src"))
from observed_portfolio import run as build_observed  # noqa: E402

FROZEN_SOURCE = SOURCE_DIR / "data/raw/icetex-dugh-vkir-2026-11-10.json"


def run(as_of="2026-11-10", source_json=FROZEN_SOURCE, output=None):
    as_of = date.fromisoformat(as_of)
    if output is None:
        with tempfile.TemporaryDirectory(prefix="ifrs9-public-evidence-") as temp:
            manifest = build_observed(as_of, temp, source_json=source_json,
                                      source_last_updated="2026-10-15")
            return summarize(Path(temp), manifest)
    output = Path(output)
    manifest = build_observed(as_of, output, source_json=source_json,
                              source_last_updated="2026-10-15")
    return summarize(output, manifest)


def summarize(output, manifest):
    frame = pd.read_csv(output / "delinquency_observed.csv")
    grouped = frame.groupby(["fecha_corte", "epoca_cartera"], as_index=False).agg(
        creditos_mora_mayor_90d=("creditos_mora_mayor_90d", "sum"),
        creditos_total=("creditos_total", "sum"),
    )
    latest = grouped["fecha_corte"].max()
    latest_rows = grouped.loc[grouped.fecha_corte.eq(latest)].copy()
    latest_rows["proporcion_mora_mayor_90d"] = (
        latest_rows.creditos_mora_mayor_90d / latest_rows.creditos_total
    )
    return {
        "source": manifest["source_url"],
        "source_updated": manifest["source_last_updated"],
        "source_sha256": manifest["source_snapshot_sha256"],
        "source_rows": manifest["source_rows"],
        "rejected_rows": manifest["rejected_rows"],
        "excluded_cuts": manifest["rejected_cuts"],
        "published_rows": manifest["rows"],
        "complete_cuts": int(frame.fecha_corte.nunique()),
        "departments": int(frame.departamento.nunique()),
        "latest_observation": latest,
        "latest_by_phase": latest_rows[["epoca_cartera", "creditos_mora_mayor_90d",
                                        "creditos_total", "proporcion_mora_mayor_90d"]]
            .sort_values("epoca_cartera").to_dict(orient="records"),
        "interpretation": "Observed aggregate delinquency stock; not individual PD, default transitions, LGD, recoveries or IFRS 9 ECL.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default="2026-11-10")
    parser.add_argument("--source-json", type=Path, default=FROZEN_SOURCE)
    parser.add_argument("--output", type=Path, help="Optional directory for curated CSV and provenance manifest")
    args = parser.parse_args()
    print(json.dumps(run(args.as_of, args.source_json, args.output), ensure_ascii=False, indent=2))
