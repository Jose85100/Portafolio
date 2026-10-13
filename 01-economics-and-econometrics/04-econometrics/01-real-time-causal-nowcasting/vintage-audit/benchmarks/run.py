"""Paired Monte Carlo audit; numbers are generated, never copied into outputs."""
import csv
import hashlib
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.vintages import Config, evaluate, simulate

ROOT=Path(__file__).resolve().parents[1]
def write_csv(name, rows):
    with (ROOT/"results"/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def main():
    all_rows=[]; metrics=[]; paired=[]
    scenarios=[("main",1,.8),("no_revision",1,0.),("no_delay",0,.8),("null",0,0.)]
    for scenario,delay,revision in scenarios:
        for seed in range(30):
            rows=evaluate(Config(seed=seed,delay=delay,revision=revision))
            for row in rows: row["scenario"]=scenario
            all_rows.extend(rows)
            mse={arm:float(np.mean([r["squared_error"] for r in rows if r["arm"]==arm]))
                 for arm in sorted({r["arm"] for r in rows})}
            for arm,val in mse.items():
                metrics.append(dict(scenario=scenario,seed=seed,arm=arm,mse=val,rmse=val**.5))
            # 2x2 factorial interaction; additive decomposition is not presumed.
            paired.append(dict(scenario=scenario,seed=seed,
                total=mse["asof_ols"]-mse["final_no_delay"],
                revision=mse["asof_ols"]-mse["final_with_delay"],
                availability=mse["asof_ols"]-mse["ignore_delay"],
                interaction=mse["asof_ols"]-mse["final_with_delay"]-mse["ignore_delay"]+mse["final_no_delay"]))
    write_csv("predictions.csv",all_rows); write_csv("seed_metrics.csv",metrics); write_csv("paired.csv",paired)
    ledger,_=simulate(Config()); write_csv("release_ledger_seed0.csv",[vars(r) for r in ledger])
    summary=[]
    for scenario,_,_ in scenarios:
        for arm in sorted({r["arm"] for r in metrics}):
            vals=np.array([r["rmse"] for r in metrics if r["arm"]==arm and r["scenario"]==scenario])
            summary.append(dict(scenario=scenario,arm=arm,mean_seed_rmse=float(vals.mean()),sd_seed_rmse=float(vals.std(ddof=1))))
    write_csv("summary.csv",summary)
    uncertainty=[]
    for scenario,_,_ in scenarios:
        for component in ("total","revision","availability","interaction"):
            vals=np.array([r[component] for r in paired if r["scenario"]==scenario])
            rng=np.random.default_rng(20261012)
            boot=vals[rng.integers(0,len(vals),(2000,len(vals)))].mean(axis=1)
            uncertainty.append(dict(scenario=scenario,component=component,mean_delta_mse=float(vals.mean()),
                lower=float(np.quantile(boot,.025)),upper=float(np.quantile(boot,.975))))
    write_csv("uncertainty.csv",uncertainty)
    timings=[]
    for n in (240,480,960):
        for seed in range(3):
            tracemalloc.start(); start=time.perf_counter(); result=evaluate(Config(n=n,seed=seed))
            elapsed=time.perf_counter()-start; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
            timings.append(dict(n=n,seed=seed,seconds=elapsed,peak_traced_bytes=peak,rows=len(result)))
    write_csv("scalability.csv",timings)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for i,(scenario,_,_) in enumerate(scenarios[:2]):
        subset=[r for r in summary if r["scenario"]==scenario]
        axes[i].barh([r["arm"] for r in subset],[r["mean_seed_rmse"] for r in subset])
        axes[i].set_title(scenario+" (synthetic, 30 seeds)"); axes[i].set_xlabel("Mean seed RMSE, final y")
    fig.tight_layout(); fig.savefig(ROOT/"results/comparison.png",dpi=150); plt.close(fig)
    metadata=dict(config=dict(n=240,seeds=list(range(30)),rho=.7,beta=.8,burn_in=60,bootstrap_seed=20261012),
       python=sys.version,platform=platform.platform(),processor=platform.processor(),cpu_model=next((line.split(":",1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines() if line.startswith("model name")), "unknown") if Path("/proc/cpuinfo").exists() else "unknown",numpy=np.__version__,
       matplotlib=matplotlib.__version__,memory="tracemalloc Python allocations; not RSS/native BLAS",date="2026-10-12 America/Bogota",
       hashes={name:hashlib.sha256((ROOT/"results"/name).read_bytes()).hexdigest() for name in ("release_ledger_seed0.csv","predictions.csv")})
    (ROOT/"results/metadata.json").write_text(json.dumps(metadata,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
