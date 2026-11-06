"""Sensitivity of observed CDT stock to *hypothetical* DTF repricing."""
import argparse,csv,json,math
from datetime import date
from pathlib import Path

def calculate(sfc,rates,shock_bps=100,pass_through=(0,.5,1)):
    if not 0<=shock_bps<=10000:raise ValueError("Invalid rate shock")
    stocks={}
    for row in sfc:
        d=date.fromisoformat(row["fecha_corte"])
        if d in stocks:raise ValueError("Duplicate SFC cut")
        x=float(row["cdt"])
        if not math.isfinite(x) or x<0:raise ValueError("Invalid CDT")
        stocks[d]=x
    benchmarks={}
    for row in rates:
        k=row["mes"]
        if k in benchmarks:raise ValueError("Duplicate DTF month")
        if row["dtf_promedio"]:
            val=float(row["dtf_promedio"])
            if not math.isfinite(val) or val<0:raise ValueError("Invalid DTF")
            benchmarks[k]=val
    if not stocks:raise ValueError("No SFC records")
    d=max(stocks)
    m=d.month-3
    yr=d.year-(m<=0)
    mm=m if m>0 else m+12
    key=f"{yr:04d}-{mm:02d}"
    if key not in benchmarks:raise ValueError("No observed lagged benchmark; no synthetic fill")
    scenarios=[]
    for p in pass_through:
        if not 0<=p<=1:raise ValueError("Invalid pass-through")
        scenarios.append({"assumed_pass_through":p,
                          "annualized_increment_COP":stocks[d]*shock_bps/10000*p,
                          "evidence":"HYPOTHETICAL_INSTANTANEOUS_REPRICING"})
    return {"observation_date":d.isoformat(),"lagged_dtf_month":key,
            "observed_dtf_pct":benchmarks[key],"observed_cdt_COP":stocks[d],
            "assumed_rate_shock_bps":shock_bps,"scenarios":scenarios,
            "actual_deposit_cost_observed":False,"production_approved":False}

def run(sfc_csv,rates_csv,out):
    with Path(sfc_csv).open(newline="",encoding="utf-8-sig") as f:a=list(csv.DictReader(f))
    with Path(rates_csv).open(newline="",encoding="utf-8-sig") as f:b=list(csv.DictReader(f))
    result=calculate(a,b)
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--sfc",required=True);ap.add_argument("--rates",required=True);ap.add_argument("--out",required=True)
    z=ap.parse_args();print(json.dumps(run(z.sfc,z.rates,z.out),indent=2))
