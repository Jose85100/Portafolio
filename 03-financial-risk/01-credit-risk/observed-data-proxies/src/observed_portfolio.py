"""Fetch observable ICETEX observed education-credit data; never treat arrears share as PD."""
import argparse
import csv
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone

SOURCE_ID = "dugh-vkir"
API = "https://www.datos.gov.co/resource/dugh-vkir.json"
FIELDS = ("fecha_corte", "deptoresidencia", "cantidad_creditos_al_dia",
          "cantidad_creditos_con_mora", "cantidad_creditos_mora_mayor",
          "total_creditos", "indicador_cartera_vencida", "epoca_cartera")


def normalized(row, as_of):
    cut = date.fromisoformat(str(row["fecha_corte"])[:10])
    if cut > as_of:
        return None
    values = []
    for key in FIELDS[2:6]:
        v = float(row[key])
        if not v.is_integer() or v < 0:
            raise ValueError("Invalid count " + key)
        values.append(int(v))
    current, short, long, total = values
    if total == 0 or current + short + long != total:
        raise ValueError("Count reconciliation failed")
    dept = str(row["deptoresidencia"]).strip()
    stage = str(row.get("epoca_cartera", "")).strip().upper()
    if not dept or stage not in {"ESTUDIOS", "AMORTIZACION"}:
        raise ValueError("Missing department or portfolio phase")
    raw = row.get("indicador_cartera_vencida")
    return dict(fecha_corte=cut.isoformat(), departamento=dept, epoca_cartera=stage,
                creditos_al_dia=current, creditos_con_mora=short,
                creditos_total=total, creditos_mora_mayor_90d=long,
                proporcion_mora_mayor_90d=long / total,
                proporcion_cualquier_mora=(short + long) / total,
                indicador_cartera_vencida_fuente=raw,
                evidencia="OBSERVADO_AGREGADO", es_pd_individual=False)


def build(rows, as_of):
    result = [v for x in rows if (v := normalized(x, as_of)) is not None]
    keys = [(x["fecha_corte"], x["departamento"], x["epoca_cartera"]) for x in result]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate grain: date x department x phase")
    return sorted(result, key=lambda x: (x["fecha_corte"], x["departamento"], x["epoca_cartera"]))


def run(as_of, output, limit=5000, source_json=None, source_last_updated=None):
    if not 0 < limit < 50001:
        raise ValueError("Invalid limit")
    url = API + "?" + urllib.parse.urlencode({
        "$select": ",".join(FIELDS), "$order": "fecha_corte,deptoresidencia,epoca_cartera",
        "$limit": limit})
    if source_json is not None:
        source_bytes = pathlib.Path(source_json).read_bytes()
        raw = json.loads(source_bytes)
        if not isinstance(raw, list):
            raise ValueError("Source snapshot must contain a JSON array")
    else:
        raw, offset = [], 0
        while True:
            page_url = url + "&" + urllib.parse.urlencode({"$offset": offset})
            with urllib.request.urlopen(page_url, timeout=30) as stream:
                page = json.load(stream)
            if not isinstance(page, list):
                raise ValueError("Unexpected API response")
            raw.extend(page)
            if len(page) < limit:
                break
            offset += len(page)
            if offset > 5000000:
                raise ValueError("Unexpectedly large extraction: review API query")
        source_bytes = json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    valid, rejected = [], []
    for index, item in enumerate(raw):
        try:
            normalized(item, as_of)
            valid.append(item)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append({"source_row": index, "fecha_corte": item.get("fecha_corte"),
                             "departamento": item.get("deptoresidencia"),
                             "epoca_cartera": item.get("epoca_cartera"), "reason": str(exc)})
    # A cut with any failed row is omitted as a whole so the observed series
    # never mixes a complete reporting period with a partial one.
    invalid_cuts = sorted({str(row.get("fecha_corte", ""))[:10] for row in rejected
                           if row.get("fecha_corte")})
    usable = [item for item in valid if str(item.get("fecha_corte", ""))[:10] not in invalid_cuts]
    records = build(usable, as_of)
    dest = pathlib.Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "rejected_records.json").write_text(json.dumps(rejected, indent=2, ensure_ascii=False))
    invalid_rate = len(rejected) / len(raw) if raw else 1.0
    reason_counts = dict(sorted(Counter(item["reason"] for item in rejected).items()))
    print("Source record rejection reasons:", json.dumps(reason_counts, sort_keys=True))
    if invalid_rate > 0.10 or not records:
        raise ValueError(f"Quality gate failed: {len(rejected)} invalid in {len(raw)} rows; {invalid_rate:.2%}")
    csvpath = dest / "delinquency_observed.csv"
    with csvpath.open("w", newline="", encoding="utf-8") as stream:
        fields = ["fecha_corte", "departamento", "epoca_cartera", "creditos_al_dia",
                  "creditos_con_mora", "creditos_total",
                  "creditos_mora_mayor_90d", "proporcion_mora_mayor_90d",
                  "proporcion_cualquier_mora", "indicador_cartera_vencida_fuente",
                  "evidencia", "es_pd_individual"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    manifest = dict(dataset=SOURCE_ID, provider="ICETEX", source_url="https://www.datos.gov.co/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir",
                    api_url=url, source_last_updated=source_last_updated,
                    source_snapshot_sha256=hashlib.sha256(source_bytes).hexdigest(),
                    as_of=as_of.isoformat(),
                    extracted_at=datetime.now(timezone.utc).isoformat(),
                    rows=len(records), validated_rows=len(valid), rejected_rows=len(rejected),
                    rejected_fraction=invalid_rate, rejected_cuts=invalid_cuts,
                    valid_rows_excluded_with_rejected_cuts=len(valid) - len(usable),
                    rejection_reasons=reason_counts, source_rows=len(raw),
                    grain="date x department x portfolio phase",
                    evidence="OBSERVED_ICETEX_EDUCATION_AGGREGATE_NOT_INDIVIDUAL_PD",
                    quality_status="COMPLETE_CUTS_ONLY_WITH_EXPLICIT_QUARANTINE" if rejected else "COMPLETE",
                    sha256=hashlib.sha256(csvpath.read_bytes()).hexdigest(),
                    caveat="Aggregate delinquency stocks are not individual PD or default transitions; source observation dates are not historical publication vintages")
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=5000)
    parser.add_argument("--source-json", help="Process a frozen public-source JSON snapshot instead of querying the API")
    parser.add_argument("--source-last-updated", help="Last-updated date shown by the source catalog (YYYY-MM-DD)")
    args = parser.parse_args()
    print(json.dumps(run(date.fromisoformat(args.as_of), args.output, args.limit,
                         args.source_json, args.source_last_updated), indent=2))
