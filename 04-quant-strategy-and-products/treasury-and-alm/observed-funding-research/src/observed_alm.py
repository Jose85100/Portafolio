"""Observed SFC aggregate funding stocks and hypothetical runoff scenarios."""
import argparse,calendar,csv,hashlib,json,math
from datetime import date,datetime,timezone
from pathlib import Path
FIELDS=("fecha_corte","depositos_corriente","depositos_ahorro","cdt","cartera_creditos","creditos_vivienda","numero_oficinas")
SHOCKS={"moderado":(.05,.03,.02),"severo":(.15,.12,.08),"extremo":(.30,.25,.18)}

def quantile(x,p):
    if not x or not 0<=p<=1: raise ValueError("Invalid quantile")
    z=sorted(x);q=(len(z)-1)*p;i=int(q)
    return z[i]+(q-i)*(z[min(i+1,len(z)-1)]-z[i])

def calculate(records):
    rows={}
    for r in records:
        if not set(FIELDS).issubset(r):raise ValueError("Missing SFC fields")
        dt=date.fromisoformat(r["fecha_corte"])
        if dt.month not in (3,6,9,12) or dt.day != calendar.monthrange(dt.year,dt.month)[1]:raise ValueError("Bad quarter")
        if dt in rows:raise ValueError("Duplicate date")
        z={k:float(r[k]) for k in FIELDS[1:]}
        if any(not math.isfinite(v) or v<0 for v in z.values()):raise ValueError("Negative/nonfinite balance")
        z["funding"]=z["depositos_corriente"]+z["depositos_ahorro"]+z["cdt"]
        if z["funding"]<=0 or z["cartera_creditos"]<=0:raise ValueError("Zero exposure")
        rows[dt]=z
    if len(rows)<8:raise ValueError("At least 8 observations required")
    series=[];growth=[];prev=None;prev_date=None
    for d in sorted(rows):
        if prev_date is not None and (d.year-prev_date.year)*12+d.month-prev_date.month != 3:
            raise ValueError("Missing quarter in time series")
        z=rows[d];v=z["funding"]
        g=None if prev is None else v/prev-1
        if g is not None:growth.append(g)
        series.append({"fecha_corte":d.isoformat(),"depositos_seleccionados":v,
                       "cartera_creditos":z["cartera_creditos"],
                       "ratio_cartera_depositos":z["cartera_creditos"]/v,
                       "deposit_growth_qoq":g,"cdt_share":z["cdt"]/v,
                       "ahorro_share":z["depositos_ahorro"]/v,
                       "corriente_share":z["depositos_corriente"]/v,
                       "evidence":"OBSERVED_AGGREGATE_NOT_BANK_LCR"})
        prev=v;prev_date=d
    z=rows[max(rows)]
    scenarios=[]
    for name,(a,b,c) in SHOCKS.items():
        rem=(z["depositos_corriente"]*(1-a)+z["depositos_ahorro"]*(1-b)+z["cdt"]*(1-c))
        scenarios.append({"name":name,"assumed_total_runoff":1-rem/z["funding"],
                          "ratio_after_runoff":z["cartera_creditos"]/rem,
                          "assumption_class":"HYPOTHETICAL_NOT_OBSERVED"})
    return {"observed_quarters":len(series),"first":series[0]["fecha_corte"],
            "last":series[-1]["fecha_corte"],"latest_observed":series[-1],
            "historical_qoq_p05":quantile(growth,.05),"historical_qoq_p50":quantile(growth,.5),
            "historical_qoq_p95":quantile(growth,.95),"scenarios":scenarios,
            "historical_pit_verified":False,"production_approved":False,
            "series":series}

def run(sfc,out):
    with Path(sfc).open(newline="",encoding="utf-8-sig") as f:rows=list(csv.DictReader(f))
    result=calculate(rows);output=Path(out);output.mkdir(parents=True,exist_ok=True)
    csv_path=output/"observed_funding_quarters.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(result["series"][0]));w.writeheader();w.writerows(result["series"])
    result.pop("series")
    result.update(source_drive_id="1ufW5qhEN2Vvm5oNDYwmvv9L_NzY4YdWR",
                  source_sha256=hashlib.sha256(Path(sfc).read_bytes()).hexdigest(),
                  output_sha256=hashlib.sha256(csv_path.read_bytes()).hexdigest(),
                  generated_at_utc=datetime.now(timezone.utc).isoformat())
    (output/"observed_alm_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--sfc",required=True);a.add_argument("--out",required=True)
    args=a.parse_args();print(json.dumps(run(args.sfc,args.out),indent=2))
