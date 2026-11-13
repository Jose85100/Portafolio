"""Observed-data GARCH application on Banco de la República TRM returns."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

import numpy as np
from arch import arch_model
from scipy import stats

ROOT=Path(__file__).resolve().parent
SOURCE_FILE=ROOT/"data"/"raw"/"banrep-trm-daily-2020-2026-11-10.xml"
OUT=ROOT/"data"/"official"
TRAINING_HOLDOUT=252
LEVEL=.99


def load_trm() -> tuple[list[str],np.ndarray,dict]:
    raw=SOURCE_FILE.read_bytes()
    tree=ET.fromstring(raw)
    ns="{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}"
    observations=[]
    for obs in tree.iter(ns+"Obs"):
        dim=obs.find(ns+"ObsDimension"); val=obs.find(ns+"ObsValue")
        if dim is None or val is None: raise ValueError("Incomplete SDMX observation")
        parsed=datetime.strptime(dim.attrib["value"],"%Y%m%d").date()
        value=float(val.attrib["value"])
        if not math.isfinite(value) or value<=0: raise ValueError(f"Invalid TRM value: {parsed}")
        if parsed.weekday()<5: observations.append((parsed.isoformat(),value))
    observations.sort()
    if len({x[0] for x in observations})!=len(observations): raise ValueError("Duplicate weekday date in TRM snapshot")
    if len(observations)<TRAINING_HOLDOUT+500: raise ValueError("Too few weekday observations for the declared design")
    meta={"source":"Banco de la República, SDMX DF_TRM_DAILY_HIST",
          "source_url":"https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/ESTAT,DF_TRM_DAILY_HIST,1.0/all/ALL/?startPeriod=2020&endPeriod=2027&dimensionAtObservation=TIME_PERIOD&detail=full",
          "file":SOURCE_FILE.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),
          "observations_in_source":sum(1 for _ in tree.iter(ns+"Obs")),
          "weekday_observations_used":len(observations),"calendar_filter":"Monday-Friday",
          "first_date":observations[0][0],"last_date":observations[-1][0],
          "unit":"COP per USD; daily official TRM"}
    return [x[0] for x in observations],np.array([x[1] for x in observations],float),meta


def kupiec(hit: np.ndarray,tail: float) -> dict:
    n=len(hit);k=int(hit.sum())
    if 0<k<n:
        p=k/n
        lr=-2*((n-k)*math.log1p(-tail)+k*math.log(tail)-
               ((n-k)*math.log1p(-p)+k*math.log(p)))
        pv=float(stats.chi2.sf(lr,1))
    else: lr=float("nan");pv=float("nan")
    return {"holdout_observations":n,"exceptions":k,"expected_exceptions":n*tail,
            "exception_rate":k/n,"kupiec_uc_lr":lr,"kupiec_uc_pvalue":pv}


def main() -> dict:
    dates,trm,source=load_trm()
    returns=100*np.diff(np.log(trm))
    return_dates=dates[1:]
    holdout_n=min(TRAINING_HOLDOUT,len(returns)-500)
    cut=len(returns)-holdout_n
    training=returns[:cut]
    fitted=arch_model(training,mean="Constant",vol="GARCH",p=1,q=1,dist="t",rescale=False).fit(disp="off")
    params=fitted.params
    mu=float(params["mu"]);omega=float(params["omega"]);alpha=float(params["alpha[1]"]);beta=float(params["beta[1]"]);nu=float(params["nu"])
    var_prev=float(fitted.conditional_volatility[-1]**2)
    eps_prev=float(fitted.resid[-1])
    forecasts=[]
    for i in range(cut,len(returns)):
        variance=max(0.0,omega+alpha*eps_prev**2+beta*var_prev)
        sigma=math.sqrt(variance)
        z=stats.t.ppf(1-LEVEL,nu)*math.sqrt((nu-2)/nu)
        var_loss=-(mu+sigma*z)
        ret=float(returns[i])
        forecasts.append({"date":return_dates[i],"return_pct":ret,"sigma_forecast_pct":sigma,
                          "var99_pct":var_loss,"exception":bool(-ret>var_loss)})
        eps_prev=ret-mu;var_prev=variance
    hit=np.array([x["exception"] for x in forecasts],dtype=int)
    summary={"source":source,"series":"TRM diaria COP por USD; weekday-only log returns",
             "sample_start":dates[0],"sample_end":dates[-1],"weekday_levels":len(dates),
             "return_observations":len(returns),"training_observations":len(training),
             "holdout_start":forecasts[0]["date"],"holdout_end":forecasts[-1]["date"],
             "confidence_level":LEVEL,
             "parameters":{"mu_pct":mu,"omega":omega,"alpha1":alpha,"beta1":beta,
                           "degrees_freedom":nu,"alpha_plus_beta":alpha+beta},
             "fit_diagnostics":{"convergence_flag":int(fitted.convergence_flag),"log_likelihood":float(fitted.loglikelihood)},
             "mean_holdout_sigma_pct":float(np.mean([x["sigma_forecast_pct"] for x in forecasts])),
             "mean_holdout_var99_pct":float(np.mean([x["var99_pct"] for x in forecasts])),
             "backtest":kupiec(hit,1-LEVEL),
             "limitations":["the TRM is a reference exchange rate, not an executable investor price",
                             "calendar weekends are excluded; public holidays remain when present in the source",
                             "parameters are estimated once and held fixed during the holdout",
                             "252 observations and few 99% exceptions yield low backtest power",
                             "results do not establish hedge effectiveness or trading profitability"]}
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"garch_trm_forecasts.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(forecasts[0]));w.writeheader();w.writerows(forecasts)
    (OUT/"application_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.ticker import FuncFormatter
        plt.style.use("seaborn-v0_8-whitegrid")
        (ROOT/"reports"/"figures").mkdir(parents=True,exist_ok=True)
        x=[datetime.strptime(r["date"],"%Y-%m-%d") for r in forecasts]
        loss=-np.array([r["return_pct"] for r in forecasts]);var=np.array([r["var99_pct"] for r in forecasts])
        fig,ax=plt.subplots(figsize=(10,4.7))
        ax.plot(x,loss,color="#17324d",linewidth=.9,label="Observed TRM loss return")
        ax.plot(x,var,color="#b91c1c",linewidth=1.1,label="GARCH-t VaR 99%")
        idx=np.flatnonzero(hit)
        ax.scatter([x[i] for i in idx],loss[idx],color="#d97706",zorder=4,label="VaR exception")
        loc=mdates.AutoDateLocator(minticks=5,maxticks=8);ax.xaxis.set_major_locator(loc);ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value,_:f"{value:.1f}%"))
        ax.set(title="GARCH-t VaR on observed TRM returns: out-of-time holdout",ylabel="Daily loss / VaR",xlabel="Date")
        ax.legend();fig.tight_layout();fig.savefig(ROOT/"reports"/"figures"/"trm-garch-var99.png",dpi=170);plt.close(fig)
    except ImportError: pass
    print(json.dumps(summary,indent=2,ensure_ascii=False));return summary


if __name__=="__main__":main()
