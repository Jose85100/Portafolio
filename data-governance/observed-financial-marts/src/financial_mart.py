"""Build observed Colombian macro-credit mart from canonical Drive CSV exports.

Does NOT replace or redistribute the raw files. No patient/customer records.
Not a point-in-time historical backtest absent original publication timestamps.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

SFC_COLUMNS = ("fecha_corte", "depositos_corriente", "depositos_ahorro",
               "cdt", "cartera_creditos", "creditos_vivienda", "numero_oficinas")
RATES_COLUMNS = ("mes", "dtf_promedio", "ibr_promedio", "tib_promedio",
                 "observaciones_dtf", "observaciones_ibr", "observaciones_tib")
SFC_DRIVE_ID = "1ufW5qhEN2Vvm5oNDYwmvv9L_NzY4YdWR"
RATES_DRIVE_ID = "1Hpu_qk99U_-Hf0H3svT2GvVYWtb9EfpE"


def read_csv(path, columns):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(x not in reader.fieldnames for x in columns):
            raise ValueError("Missing required columns " + str(columns))
        return list(reader)


def parse_number(value, *, nullable=False):
    if value in ("", None) and nullable:
        return None
    v = float(value)
    if not math.isfinite(v):
        raise ValueError("Nonfinite observation")
    return v


def month_back(quarter_date):
    """Month 3 months prior to quarter-end; avoids contemporaneous overlap."""
    year = quarter_date.year
    month = quarter_date.month - 3
    if month <= 0:
        year -= 1
        month += 12
    return f"{year:04d}-{month:02d}"


def compute(sfc, rates):
    observations = {}
    for row in sfc:
        key = date.fromisoformat(row["fecha_corte"])
        if key.month not in (3, 6, 9, 12):
            raise ValueError("Non-quarterly SFC period")
        if key in observations:
            raise ValueError("Duplicate SFC quarter")
        vals = {c: parse_number(row[c]) for c in SFC_COLUMNS[1:]}
        if any(v < 0 for v in vals.values()) or vals["cartera_creditos"] <= 0:
            raise ValueError("Invalid credit balance or negative value")
        observations[key] = vals
    m_rates = {}
    for row in rates:
        key = row["mes"]
        if len(key) != 7 or key[4] != "-" or not 1 <= int(key[5:]) <= 12 or key in m_rates:
            raise ValueError("Invalid or repeated monthly rate")
        values = {c: parse_number(row[c], nullable=True) for c in RATES_COLUMNS[1:4]}
        counts = {c: int(row[c]) for c in RATES_COLUMNS[4:]}
        if any(v < 0 for v in counts.values()):
            raise ValueError("Negative observation count")
        for rate_name, count_name in zip(RATES_COLUMNS[1:4], RATES_COLUMNS[4:]):
            if (values[rate_name] is None) != (counts[count_name] == 0):
                raise ValueError("Rate availability inconsistent with source observation count")
        m_rates[key] = values
    quarters = sorted(observations)
    if not quarters:
        raise ValueError("No SFC observations")
    outputs = []
    for i, q in enumerate(quarters):
        x = observations[q]
        deposits = x["depositos_corriente"] + x["depositos_ahorro"] + x["cdt"]
        if deposits <= 0:
            raise ValueError("Zero deposits denominator")
        year_ago = observations.get(date(q.year - 1, q.month, q.day))
        yoy = None if year_ago is None else 100 * (x["cartera_creditos"] / year_ago["cartera_creditos"] - 1)
        # Values are observed stock measures and derived ratios, not individual default outcomes.
        rate_key = month_back(q)
        rate = m_rates.get(rate_key, {})
        outputs.append({
            "fecha_corte": q.isoformat(),
            "cartera_sobre_depositos": x["cartera_creditos"] / deposits,
            "crecimiento_cartera_yoy_pct": yoy,
            "participacion_vivienda_cartera": x["creditos_vivienda"] / x["cartera_creditos"],
            "mes_ibr_rezagado": rate_key,
            "ibr_rezagado_pct": rate.get("ibr_promedio"),
            "dtf_rezagada_pct": rate.get("dtf_promedio"),
            "source_class": "OBSERVED_AGGREGATE_DERIVED",
            "is_obligor_pd": False,
        })
    return outputs


def pearson(a, b):
    if len(a) < 4 or len(a) != len(b):
        return None
    am, bm = sum(a) / len(a), sum(b) / len(b)
    xy = sum((x - am) * (y - bm) for x, y in zip(a, b))
    xx = sum((x - am) ** 2 for x in a)
    yy = sum((y - bm) ** 2 for y in b)
    return xy / math.sqrt(xx * yy) if xx > 0 and yy > 0 else None


def execute(sfc_path, rates_path, outdir):
    sfc = read_csv(sfc_path, SFC_COLUMNS)
    rates = read_csv(rates_path, RATES_COLUMNS)
    rows = compute(sfc, rates)
    valid = [(r["ibr_rezagado_pct"], r["crecimiento_cartera_yoy_pct"])
             for r in rows if r["ibr_rezagado_pct"] is not None
             and r["crecimiento_cartera_yoy_pct"] is not None]
    dest = Path(outdir)
    dest.mkdir(parents=True, exist_ok=True)
    result_file = dest / "observed_macro_credit_mart.csv"
    with result_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "source_drives": [SFC_DRIVE_ID, RATES_DRIVE_ID],
        "data_owner": "Master_DATOS (Drive): no copies of canonical RAW in Git",
        "sfc_rows": len(sfc), "banrep_months": len(rates),
        "mart_rows": len(rows), "paired_yoy_ibr_rows": len(valid),
        "min_quarter": rows[0]["fecha_corte"], "max_quarter": rows[-1]["fecha_corte"],
        "last_credit_deposit_ratio": rows[-1]["cartera_sobre_depositos"],
        "last_credit_yoy_pct": rows[-1]["crecimiento_cartera_yoy_pct"],
        "pearson_credit_growth_ibr_lagged": pearson(
            [x[0] for x in valid], [x[1] for x in valid]),
        "source_sha256": {label: hashlib.sha256(Path(p).read_bytes()).hexdigest()
                          for label, p in (("sfc", sfc_path), ("banrep_rates", rates_path))},
        "mart_sha256": hashlib.sha256(result_file.read_bytes()).hexdigest(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "historical_pit_verified": False,
        "limitations": [
            "Dates are periods of observation, not original publication dates; no backtest with as-known-at guarantees.",
            "Credit balances and deposit stocks are aggregates, not individual loan PD/LGD/EAD.",
            "Rate is from the third preceding calendar month; correlation is descriptive and not causal.",
            "Current and historical revisions, nominal units and data-provider methodologies need independent validation.",
        ],
    }
    (dest / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sfc", required=True, help="Local canonical Drive SFC CSV export")
    parser.add_argument("--rates", required=True, help="Local canonical Drive BanRep monthly CSV export")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(json.dumps(execute(args.sfc, args.rates, args.out), indent=2, ensure_ascii=False))
