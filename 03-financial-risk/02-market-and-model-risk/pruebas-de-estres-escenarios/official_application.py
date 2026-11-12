"""Observed historical stress and reverse-stress for a Treasury-rate factor."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parent
VAR_PROJECT=ROOT.parent/"var-es-tres-metodos"
sys.path.insert(0,str(VAR_PROJECT))
from official_version import load_observations  # noqa: E402

DURATION=8.0
NOTIONAL=10_000_000.0
LOSS_TARGET=0.10
OUT=ROOT/"data"/"official"


def main() -> dict:
    dates,yield_pct,hashes=load_observations()
    delta_pct=np.diff(yield_pct)
    delta_bp=delta_pct*100
    losses= DURATION*(delta_pct/100)*NOTIONAL
    rows=[{"date":dates[i+1],"yield_change_bp":float(delta_bp[i]),
           "long_bond_loss_usd":float(losses[i]),
           "long_bond_loss_pct_notional":float(losses[i]/NOTIONAL)}
          for i in range(len(delta_bp))]
    worst=sorted(rows,key=lambda row:row["long_bond_loss_usd"],reverse=True)[:10]
    max_up=max(rows,key=lambda row:row["yield_change_bp"])
    max_down=min(rows,key=lambda row:row["yield_change_bp"])
    reverse_shock_bp=LOSS_TARGET/DURATION*10000
    hit_count=sum(row["long_bond_loss_pct_notional"]>=LOSS_TARGET for row in rows)
    summary={"source_period_start":dates[0],"source_period_end":dates[-1],
             "yield_observations":len(dates),"daily_changes":len(rows),
             "duration_assumption_years":DURATION,"notional_usd":NOTIONAL,
             "worst_long_bond_shocks":worst,
             "largest_yield_increase":max_up,"largest_yield_decrease":max_down,
             "reverse_stress_loss_target_pct":LOSS_TARGET*100,
             "required_yield_increase_bp":reverse_shock_bp,
             "historical_days_meeting_target":hit_count,
             "source_hashes":hashes,
             "interpretation":"single-factor duration proxy, not a multi-factor portfolio valuation",
             "limitations":["no convexity, carry, roll-down, coupon cash flows or basis risk",
                            "the observation period is 2024 through 2026 and does not include 2008 or 2020 crises",
                            "absence of a hit in this sample does not imply the reverse-stress target is implausible"]}
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"daily_rate_shocks.csv").open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (OUT/"stress_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.ticker import FuncFormatter
        from datetime import datetime
        plt.style.use("seaborn-v0_8-whitegrid")
        FIG=ROOT/"reports"/"figures";FIG.mkdir(parents=True,exist_ok=True)
        x=[datetime.strptime(row["date"],"%Y-%m-%d") for row in rows]
        pnl=np.array([row["long_bond_loss_usd"] for row in rows])
        fig,ax=plt.subplots(figsize=(10,4.6))
        ax.bar(x,pnl,color=np.where(pnl>0,"#b91c1c","#2463eb"),width=1.0)
        ax.axhline(LOSS_TARGET*NOTIONAL,color="#d97706",linestyle="--",label="Reverse-stress target: 10% notional")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value,_: f"${value/1000:,.0f}k"))
        loc=mdates.AutoDateLocator(minticks=5,maxticks=8)
        ax.xaxis.set_major_locator(loc);ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
        ax.set(title="Observed 10-year rate-shock P&L proxy by day",ylabel="Long-position loss / gain (USD 10m exposure)",xlabel="Date")
        ax.legend();fig.tight_layout();fig.savefig(FIG/"treasury-historical-stress.png",dpi=170);plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(summary,indent=2))
    return summary


if __name__=="__main__":main()
