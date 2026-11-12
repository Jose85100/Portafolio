"""Kupiec and Christoffersen tests on observed Treasury rate-shock P&L proxy."""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parent
VAR_PROJECT = ROOT.parent / "var-es-tres-metodos"
sys.path.insert(0, str(VAR_PROJECT))
from main import historico  # noqa: E402
from official_version import load_observations  # noqa: E402

TRAINING = 500
LEVEL = 0.99
DURATION = 8.0
OUT = ROOT / "data" / "official"


def likelihood(pi: float, failures: int, successes: int) -> float:
    pi = min(max(pi, 1e-12), 1 - 1e-12)
    return failures * math.log1p(-pi) + successes * math.log(pi)


def tests(hit: np.ndarray, tail: float) -> dict:
    n = int(len(hit)); k = int(hit.sum()); phat = k / n
    lr_uc = -2 * (likelihood(tail, n-k, k) - likelihood(phat, n-k, k))
    n00 = n01 = n10 = n11 = 0
    for previous, current in zip(hit[:-1], hit[1:]):
        if previous == 0 and current == 0: n00 += 1
        elif previous == 0 and current == 1: n01 += 1
        elif previous == 1 and current == 0: n10 += 1
        else: n11 += 1
    p01 = n01 / (n00+n01) if n00+n01 else phat
    p11 = n11 / (n10+n11) if n10+n11 else phat
    pooled = (n01+n11) / max(n00+n01+n10+n11, 1)
    ll_independent = likelihood(pooled, n00+n10, n01+n11)
    ll_markov = likelihood(p01, n00, n01) + likelihood(p11, n10, n11)
    lr_ind = max(0.0, -2 * (ll_independent - ll_markov))
    return {"observations": n, "exceptions": k, "expected_exceptions": n*tail,
            "exception_rate": phat, "kupiec_uc_lr": lr_uc,
            "kupiec_uc_pvalue": float(chi2.sf(lr_uc, 1)),
            "christoffersen_ind_lr": lr_ind,
            "christoffersen_ind_pvalue": float(chi2.sf(lr_ind, 1)),
            "n00": n00, "n01": n01, "n10": n10, "n11": n11}


def main() -> dict:
    dates, yields_pct, hashes = load_observations()
    returns = -DURATION * np.diff(yields_pct) / 100.0
    observation_dates = dates[1:]
    holdout_start = max(TRAINING, len(returns)-252)
    losses = -returns
    forecast_rows = []
    for i in range(holdout_start, len(returns)):
        var, es = historico(returns[i-TRAINING:i], LEVEL)
        forecast_rows.append({"date": observation_dates[i], "loss_return": float(losses[i]),
                              "var_return": var, "es_return": es,
                              "exception": bool(losses[i] > var)})
    hit = np.array([row["exception"] for row in forecast_rows], dtype=int)
    result = tests(hit, 1-LEVEL)
    result.update({"source_period_start": dates[0], "source_period_end": dates[-1],
                   "holdout_start": forecast_rows[0]["date"], "holdout_end": forecast_rows[-1]["date"],
                   "training_window": TRAINING, "confidence_level": LEVEL,
                   "duration_assumption_years": DURATION, "source_hashes": hashes,
                   "scope_note": "single-factor first-order duration proxy; not an observed bond return series"})
    OUT.mkdir(parents=True, exist_ok=True)
    (ROOT/"reports"/"figures").mkdir(parents=True, exist_ok=True)
    with (OUT/"exceptions.csv").open("w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(forecast_rows[0]));writer.writeheader();writer.writerows(forecast_rows)
    (OUT/"backtest.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        plt.style.use("seaborn-v0_8-whitegrid")
        fig,ax=plt.subplots(figsize=(10,4.5))
        x=[datetime.strptime(row["date"],"%Y-%m-%d") for row in forecast_rows]
        realized=np.array([row["loss_return"] for row in forecast_rows])*1_000_000
        var=np.array([row["var_return"] for row in forecast_rows])*1_000_000
        ax.plot(x,realized,color="#17324d",linewidth=.9,label="Realized duration proxy")
        ax.plot(x,var,color="#b91c1c",linewidth=1,label="Rolling historical VaR 99%")
        idx=np.flatnonzero(hit)
        ax.scatter([x[i] for i in idx],realized[idx],color="#d97706",zorder=4,label="VaR exception")
        locator=mdates.AutoDateLocator(minticks=5,maxticks=8)
        ax.xaxis.set_major_locator(locator);ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax.set(title="Observed 10-year yield-shock P&L proxy and rolling VaR 99%",
               ylabel="USD per USD 1m exposure",xlabel="Out-of-time date")
        ax.legend();fig.tight_layout()
        fig.savefig(ROOT/"reports"/"figures"/"treasury-var-kupiec-christoffersen.png",dpi=170)
        plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(result,indent=2))
    return result


if __name__ == "__main__": main()
