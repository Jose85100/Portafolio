"""Fetch observable ICETEX observed education-credit data; never treat arrears share as PD."""
import argparse
import csv
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request
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
    stage = str(row.get("epoca_cartera", "")).strip()
    if not dept or not stage:
        raise ValueError("Missing department or portfolio phase")
    raw = row.get("indicador_cartera_vencida")
    return dict(fecha_corte=cut.isoformat(), departamento=dept, epoca_cartera=stage,
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


def run(as_of, output, limit=5000):
    if not 0 < limit < 50001:
        raise ValueError("Invalid limit")
    url = API + "?" + urllib.parse.urlencode({
        "$select": ",".join(FIELDS), "$order": "fecha_corte,deptoresidencia,epoca_cartera",
        "$limit": limit})
    raw = []
    offset = 0
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
    valid, rejected = [], []
    for index, item in enumerate(raw):
        try:
            normalized(item, as_of)
            valid.append(item)
        except (ValueError, KeyError, TypeError) as exc:
            rejected.append({"source_row": index, "fecha_corte": item.get("fecha_corte"),
                             "departamento": item.get("deptoresidencia"),
                             "epoca_cartera": item.get("epoca_cartera"), "reason": str(exc)})
    records = build(valid, as_of)
    dest = pathlib.Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "rejected_records.json").write_text(json.dumps(rejected, indent=2, ensure_ascii=False))
    invalid_rate = len(rejected) / len(raw) if raw else 1.0
    if invalid_rate > 0.10 or not records:
        raise ValueError(f"Quality gate failed: {len(rejected)} invalid in {len(raw)} rows; {invalid_rate:.2%}")
    csvpath = dest / "delinquency_observed.csv"
    with csvpath.open("w", newline="", encoding="utf-8") as stream:
        fields = ["fecha_corte", "departamento", "epoca_cartera", "creditos_total",
                  "creditos_mora_mayor_90d", "proporcion_mora_mayor_90d",
                  "proporcion_cualquier_mora", "indicador_cartera_vencida_fuente",
                  "evidencia", "es_pd_individual"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    manifest = dict(dataset=SOURCE_ID, url=url, as_of=as_of.isoformat(),
                    extracted_at=datetime.now(timezone.utc).isoformat(),
                    rows=len(records), rejected_rows=len(rejected), rejected_fraction=invalid_rate, source_rows=len(raw), grain="date x department x portfolio phase",
                    evidence="OBSERVED_ICETEX_EDUCATION_AGGREGATE_NOT_PD",
                    provider="ICETEX",
                    sha256=hashlib.sha256(csvpath.read_bytes()).hexdigest(),
                    caveat="Date cutoff is not historical publication-vintage validation")
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()
    print(json.dumps(run(date.fromisoformat(args.as_of), args.output, args.limit), indent=2))
