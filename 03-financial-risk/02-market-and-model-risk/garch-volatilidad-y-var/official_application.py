"""Fit Student-t GARCH(1,1) on Treasury duration-proxy returns and forecast OOS."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from arch import arch_model
from scipy import stats

ROOT=Path(__file__).resolve().parent
VAR_PROJECT=ROOT.parent/"var-es-tres-metodos"
sys.path.insert(0,str(VAR_PROJECT))
from official_version import load_observations  # noqa: E402

TRAINING=500
HOLDOUT=252
LEVEL=.99
DURATION=8.0
OUT=ROOT/"data"/"official"


def backtest(hit: np.ndarray) -> dict:
    n=len(hit);k=int(hit.sum());tail=1-LEVEL
    if 0<k<n:
        p=k/n
        lr=-2*((n-k)*math.log(1-tail)+k*math.log(tail)-
               ((n-k)*math.log1p(-p)+k*math.log(p)))
        pv=float(stats.chi2.sf(lr,1))
    else:
        lr=float("nan");pv=float("nan")
    return {"holdout_observations":n,"exceptions":k,"expected_exceptions":n*tail,
            "exception_rate":k/n,"kupiec_uc_lr":lr,"kupiec_uc_pvalue":pv}


def main() -> dict:
    dates,yield_pct,hashes=load_observations()
    # Scale decimal duration returns to percentage points for numerical stability.
    returns_pct=-DURATION*np.diff(yield_pct)
    obs_dates=dates[1:]
    holdout_n=min(HOLDOUT,len(returns_pct)-TRAINING)
    start=len(returns_pct)-holdout_n
    train=returns_pct[:start]
    fitted=arch_model(train,mean="Constant",vol="GARCH",p=1,q=1,dist="t",rescale=False).fit(disp="off")
    p=fitted.params
    mu=float(p["mu"]);omega=float(p["omega"]);alpha=float(p["alpha[1]"]);beta=float(p["beta[1]"]);nu=float(p["nu"])
    conditional_var=float(fitted.conditional_volatility[-1]**2)
    last_resid=float(fitted.resid[-1])
    forecast_rows=[]
    for i in range(start,len(returns_pct)):
        h=omega+alpha*last_resid**2+beta*conditional_var
        sigma=math.sqrt(max(h,0))
        quantile=stats.t.ppf(1-LEVEL,nu)*math.sqrt((nu-2)/nu)
        var_pct=-(mu+sigma*quantile)
        realized=float(returns_pct[i])
        forecast_rows.append({"date":obs_dates[i],"return_pct":realized,"conditional_sigma_pct":sigma,
                              "var99_pct":var_pct,"exception":bool(-realized>var_pct)})
        last_resid=realized-mu
        conditional_var=h
    hit=np.array([row["exception"] for row in forecast_rows],dtype=int)
    result={"source_period_start":dates[0],"source_period_end":dates[-1],
            "holdout_start":forecast_rows[0]["date"],"holdout_end":forecast_rows[-1]["date"],
            "training_observations":len(train),"holdout_observations":holdout_n,
            "series":"U.S. Treasury daily 10-year par yield change; fixed-duration P&L proxy",
            "duration_assumption_years":DURATION,"confidence_level":LEVEL,
            "parameters":{"mu_pct":mu,"omega":omega,"alpha1":alpha,"beta1":beta,"degrees_freedom":nu,
                          "alpha_plus_beta":alpha+beta},
            "fit_diagnostics":{"convergence_flag":int(fitted.convergence_flag),
                               "log_likelihood":float(fitted.loglikelihood)},
            "mean_forecast_sigma_pct":float(np.mean([r["conditional_sigma_pct"] for r in forecast_rows])),
            "mean_forecast_var99_pct":float(np.mean([r["var99_pct"] for r in forecast_rows])),
            "backtest":backtest(hit),"source_hashes":hashes,
            "limitations":["parameters fixed after initial estimation; conditional variance updates with realized proxy returns",
                            "daily par-yield changes are not bond total returns",
                            "214 observations and few 99% exceptions provide limited backtest power",
                            "no convexity, carry, roll-down, portfolio positions or basis risk"]}
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"garch_forecasts.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(forecast_rows[0]));writer.writeheader();writer.writerows(forecast_rows)
    (OUT/"garch_summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        plt.style.use("seaborn-v0_8-whitegrid")
        (ROOT/"reports"/"figures").mkdir(parents=True,exist_ok=True)
        x=[datetime.strptime(r["date"],"%Y-%m-%d") for r in forecast_rows]
        sigma=np.array([r["conditional_sigma_pct"] for r in forecast_rows])
        var=np.array([r["var99_pct"] for r in forecast_rows])
        realized=np.array([-r["return_pct"] for r in forecast_rows])
        fig,ax=plt.subplots(figsize=(10,4.6))
        ax.plot(x,sigma,color="#245b72",label="GARCH conditional sigma")
        ax.plot(x,var,color="#b91c1c",label="Student-t VaR 99%")
        ax.scatter([x[i] for i in np.flatnonzero(hit)],realized[hit.astype(bool)],color="#d97706",label="Exception",zorder=4)
        loc=mdates.AutoDateLocator(minticks=5,maxticks=8);ax.xaxis.set_major_locator(loc);ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
        ax.set(title="GARCH(1,1)-t: observed yield-shock proxy and conditional risk",ylabel="Percent of notional",xlabel="Holdout date")
        ax.legend();fig.tight_layout();fig.savefig(ROOT/"reports"/"figures"/"treasury-garch-var99.png",dpi=170);plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(result,indent=2));return result


if __name__=="__main__":main()
