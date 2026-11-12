"""Apply entity-disjoint split policies to official WDI country-indicator rows."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.splitter import Record, leaked_components, split

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
WDI=REPO/"02-mathematics-statistics-and-quant/quantitative-methods/analisis-factorial-multiple-mfa/datos"
LONG=WDI/"indicadores_wb_largo.csv"
META=WDI/"paises_meta.csv"
OUT=ROOT/"results"/"official-wdi"
SOURCE="https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
SEEDS=range(100)
MIN_COVERAGE=.85


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    economy_codes=set()
    with META.open(newline="",encoding="utf-8") as stream:
        for row in csv.DictReader(stream): economy_codes.add(row["iso3"])
    country_indicators=defaultdict(set)
    with LONG.open(newline="",encoding="utf-8") as stream:
        reader=csv.DictReader(stream)
        required={"iso3","codigo","valor","anio"}
        if not required.issubset(reader.fieldnames or []): raise ValueError("Unexpected WDI long-file schema")
        for row in reader:
            iso=row["iso3"].strip(); code=row["codigo"].strip()
            if iso not in economy_codes: continue
            if not code or not row["valor"].strip(): raise ValueError("Missing indicator key or value")
            key=(iso,code)
            if code in country_indicators[iso]: raise ValueError(f"Duplicate country-indicator record: {key}")
            country_indicators[iso].add(code)
    indicators=len({code for codes in country_indicators.values() for code in codes})
    eligible={iso:codes for iso,codes in country_indicators.items() if len(codes)/indicators>=MIN_COVERAGE}
    records=[]; rows_by_country=defaultdict(list)
    for iso,codes in sorted(eligible.items()):
        for code in sorted(codes):
            rid=f"{iso}:{code}"
            records.append(Record(rid,(iso,)))
            rows_by_country[iso].append(rid)
    if not records or not eligible: raise ValueError("No eligible WDI country-indicator records")

    results=[]
    for seed in SEEDS:
        for mode in ("row","component"):
            assignment=split(records,mode=mode,seed=seed)
            cut_entities=[iso for iso,ids in rows_by_country.items()
                          if {assignment[rid] for rid in ids}=={"train","test"}]
            exposed=sum(len(rows_by_country[iso]) for iso in cut_entities)
            results.append({"seed":seed,"policy":mode,"records":len(records),
                            "entities":len(eligible),"train_rows":sum(v=="train" for v in assignment.values()),
                            "test_rows":sum(v=="test" for v in assignment.values()),
                            "countries_split_across_sides":len(cut_entities),"rows_in_split_countries":exposed})
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"seed_results.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    summary={}
    for mode in ("row","component"):
        subset=[r for r in results if r["policy"]==mode]
        summary[mode]={"runs":len(subset),"mean_countries_split":sum(r["countries_split_across_sides"] for r in subset)/len(subset),
                       "min_countries_split":min(r["countries_split_across_sides"] for r in subset),
                       "max_countries_split":max(r["countries_split_across_sides"] for r in subset),
                       "mean_rows_exposed":sum(r["rows_in_split_countries"] for r in subset)/len(subset),
                       "runs_with_zero_split_countries":sum(r["countries_split_across_sides"]==0 for r in subset)}
    manifest={"source_provider":"World Bank","dataset":"World Development Indicators",
              "source_api":SOURCE,"source_window":"2015-2022; latest available within the window per country-indicator",
              "source_extraction_timestamp_recorded":False,"source_snapshot_is_preexisting_repository_data":True,
              "input_files":{"indicator_observations":{"path":"02-mathematics-statistics-and-quant/quantitative-methods/analisis-factorial-multiple-mfa/datos/indicadores_wb_largo.csv","sha256":sha(LONG),"bytes":LONG.stat().st_size},
                             "economy_metadata":{"path":"02-mathematics-statistics-and-quant/quantitative-methods/analisis-factorial-multiple-mfa/datos/paises_meta.csv","sha256":sha(META),"bytes":META.stat().st_size}},
              "source_records_in_long_file":sum(1 for _ in csv.DictReader(LONG.open(encoding="utf-8"))),
              "nonaggregate_economies_in_metadata":len(economy_codes),"indicators":indicators,
              "coverage_threshold":MIN_COVERAGE,"eligible_countries":len(eligible),
              "eligible_observed_country_indicator_rows":len(records),
              "grain":"country ISO3 × WDI indicator code; one latest available value within 2015-2022",
              "entity_identity":"official ISO3 country code; known identity, no record linkage inferred",
              "seeds":len(SEEDS),"summary":summary,
              "interpretation":"measures split integrity for multirow country entities; not predictive quality or entity-resolution accuracy",
              "limitations":["WDI snapshot has no recorded API extraction timestamp or revision vintage",
                             "country-indicator rows have no prediction target; this is a partition-integrity audit only",
                             "country identities are authoritative ISO3 keys, not ambiguous applicant/company links",
                             "coverage threshold selects a subset and does not remove missingness bias"]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        fig,ax=plt.subplots(figsize=(8.5,4.5))
        means=[summary[m]["mean_countries_split"] for m in ("row","component")]
        bars=ax.bar(["Row-level random split","Country-component split"],means,color=["#d97706","#167c80"])
        for bar,value in zip(bars,means):ax.text(bar.get_x()+bar.get_width()/2,value+2,f"{value:.0f} countries",ha="center")
        ax.set(title="Official WDI records: country identity crossing train and test",
               ylabel="Mean split countries across 100 deterministic seeds",ylim=(0,max(means)*1.18 if max(means)>0 else 1))
        fig.tight_layout();fig.savefig(OUT/"wdi-country-split-leakage.png",dpi=170);plt.close(fig)
    except ImportError:pass
    print(json.dumps(manifest,indent=2))
    return manifest


if __name__=="__main__":main()
