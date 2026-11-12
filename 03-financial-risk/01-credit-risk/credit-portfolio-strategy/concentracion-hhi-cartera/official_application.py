"""HHI application to official SFC balances by supervised lender and product."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parent
RAW=ROOT/"data"/"raw"/"sfc-distribucion-cartera-producto-2024-2026.json"
OUT=ROOT/"data"/"official"
FIG=ROOT/"reports"/"figures"
SOURCE_PAGE="https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8"
SOURCE_API="https://www.datos.gov.co/resource/rvii-eis8.json"
PRODUCTS={"1":"CRÉDITO ROTATIVO","2":"TARJETAS DE CRÉDITO","4":"LIBRANZA","9":"VIVIENDA VIS PESOS"}


def main() -> dict:
    raw=RAW.read_bytes()
    rows=json.loads(raw)
    df=pd.DataFrame(rows)
    required={"fecha_corte","tipo_entidad","codigo_entidad","nombreentidad","unicap","descrip_uc","renglon","desc_renglon","_1_saldo_de_la_cartera_a"}
    if not required.issubset(df.columns):
        raise ValueError(f"Source schema missing: {sorted(required-set(df.columns))}")
    df=df.rename(columns={"_1_saldo_de_la_cartera_a":"saldo_bruto"})
    df["fecha_corte"]=pd.to_datetime(df["fecha_corte"],utc=True,errors="coerce").dt.date.astype("string")
    for col in ("tipo_entidad","codigo_entidad","unicap","renglon"):
        df[col]=df[col].astype("string").str.strip()
    df["saldo_bruto"]=pd.to_numeric(df["saldo_bruto"],errors="coerce")
    df["desc_renglon"]=df["desc_renglon"].astype("string").str.strip().str.upper()
    invalid_date=int(df["fecha_corte"].isna().sum())
    invalid_balance=int((~df["saldo_bruto"].map(math.isfinite)).sum())
    negative=int((df["saldo_bruto"]<0).sum())
    non_total=int((~df["desc_renglon"].str.contains("TOTAL",regex=False,na=False)).sum())
    key=["fecha_corte","tipo_entidad","codigo_entidad","unicap"]
    duplicates=int(df.duplicated(key,keep=False).sum())
    if invalid_date or invalid_balance or negative or non_total or duplicates:
        raise ValueError(f"Quality gate failed: invalid dates={invalid_date}, nonnumeric balances={invalid_balance}, negative balances={negative}, non-total rows={non_total}, duplicate key rows={duplicates}")
    df["institution_id"]=df["tipo_entidad"]+":"+df["codigo_entidad"]
    # Concentration is calculated separately inside each product and cut.
    records=[]
    for (cut,unicap),g in df.groupby(["fecha_corte","unicap"],sort=True):
        amounts=g.groupby("institution_id",sort=False)["saldo_bruto"].sum()
        total=float(amounts.sum())
        if not math.isfinite(total) or total<=0:
            raise ValueError(f"Nonpositive market balance for {cut}, product {unicap}")
        shares=amounts/total
        sorted_shares=shares.sort_values(ascending=False)
        records.append({"fecha_corte":str(cut),"unicap":str(unicap),
                        "producto":str(g["descrip_uc"].mode().iloc[0]),
                        "entidades":int(len(amounts)),"saldo_total":total,
                        "hhi_10000":float((shares**2).sum()*10000),
                        "numero_efectivo_entidades":float(1/(shares**2).sum()),
                        "participacion_top1":float(sorted_shares.iloc[0]),
                        "participacion_top5":float(sorted_shares.head(5).sum())})
    result=pd.DataFrame(records)
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    processed=OUT/"hhi_by_product_and_cut.csv"
    result.to_csv(processed,index=False,float_format="%.10g")
    latest=str(df["fecha_corte"].max())
    latest_products=result[result["fecha_corte"]==latest].copy()
    selected=latest_products[latest_products["unicap"].isin(PRODUCTS)].copy()
    manifest={"source_provider":"Superintendencia Financiera de Colombia",
              "source_page":SOURCE_PAGE,"source_api":SOURCE_API,"dataset_id":"rvii-eis8",
              "extraction_filter":"fecha_corte >= 2024-01-01 AND desc_renglon LIKE '%TOTAL%'",
              "selected_fields":sorted(required),
              "data_last_updated":"2026-10-23","latest_source_cut":latest,
              "extraction_cut":"2026-11-10","period_start":str(df["fecha_corte"].min()),
              "period_end":latest,"raw_rows":len(df),"cuts":int(df["fecha_corte"].nunique()),
              "institution_product_cut_rows":len(df),"quality":{"invalid_dates":invalid_date,
              "nonnumeric_balances":invalid_balance,"negative_balances":negative,
              "non_total_rows":non_total,"duplicate_key_rows":duplicates},
              "raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_bytes":len(raw),
              "processed_sha256":hashlib.sha256(processed.read_bytes()).hexdigest(),
              "processed_rows":len(result),"metric":"HHI=10,000*sum(entity balance share squared), within product and cut",
              "institution_key":"tipo_entidad:codigo_entidad",
              "limitations":["HHI covers lender concentration, not borrower or sector concentration",
              "public product balances are not account-level exposures or internal obligor limits",
              "source totals can contain repeated category spellings; product code UNICAP is used as the grouping key",
              "does not estimate credit default risk, expected loss, systemic contagion or regulatory concentration limits"]}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    latest_products.to_csv(OUT/"latest_cut_by_product.csv",index=False,float_format="%.10g")
    (OUT/"latest_cut_by_product.json").write_text(selected.to_json(orient="records",indent=2,force_ascii=False)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        plt.style.use("seaborn-v0_8-whitegrid")
        fig,ax=plt.subplots(figsize=(9.5,4.8))
        for code,label in PRODUCTS.items():
            p=result[result["unicap"]==code]
            ax.plot(pd.to_datetime(p["fecha_corte"]),p["hhi_10000"],marker="o",markersize=2.5,linewidth=1.5,label=label)
        ax.set(title="Concentración de saldos entre entidades, por producto",ylabel="HHI (escala 0–10.000)",xlabel="Corte mensual")
        ax.legend(ncol=2,fontsize=8);fig.tight_layout();fig.savefig(FIG/"sfc-lender-hhi-trend.png",dpi=170);plt.close(fig)
        fig,ax=plt.subplots(figsize=(9.5,4.8))
        selected=selected.sort_values("hhi_10000",ascending=True)
        bars=ax.barh(selected["producto"],selected["hhi_10000"],color="#167c80")
        for bar,value in zip(bars,selected["hhi_10000"]):
            ax.text(value+25,bar.get_y()+bar.get_height()/2,f"{value:,.0f}",va="center",fontsize=9)
        ax.set_xlim(0,float(selected["hhi_10000"].max())*1.18)
        ax.set(title=f"HHI por entidad en el último corte disponible ({latest})",xlabel="HHI (escala 0–10.000)",ylabel="Producto")
        fig.tight_layout();fig.savefig(FIG/"sfc-lender-hhi-latest.png",dpi=170);plt.close(fig)
    except ImportError:
        pass
    summary={"latest_cut":latest,"cuts":int(df["fecha_corte"].nunique()),"source_rows":len(df),
             "quality":manifest["quality"],"selected_products":selected.to_dict(orient="records")}
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary


if __name__=="__main__":main()
