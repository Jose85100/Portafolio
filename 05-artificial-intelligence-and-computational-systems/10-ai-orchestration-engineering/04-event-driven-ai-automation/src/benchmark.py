"""Benchmark paired: 30 seeds x 3 regimes x 3 policies."""
from __future__ import annotations
import csv, json, math, platform, sqlite3, statistics, time
from pathlib import Path
from .experiment import make_workload, run

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/"results"
REGIMES={"low_duplicate":(0.10,0.10),"burst_duplicate":(0.60,0.15),"high_fault":(0.30,0.60)}
POLICIES=("naive","inbox","inbox_no_retry")

def main():
    RESULTS.mkdir(exist_ok=True)
    t0=time.perf_counter()
    rows=[]
    for regime,(dup,fault) in REGIMES.items():
        for seed in range(30):
            w=make_workload(seed,n=120,duplicate_rate=dup,fault_rate=fault,invalid_rate=0.05,conflict_rate=0.05)
            for policy in POLICIES:
                rows.append({"regime":regime,"seed":seed,**run(w,policy)})
    with (RESULTS/"raw.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary=[]
    for regime in REGIMES:
        for policy in POLICIES:
            group=[r for r in rows if r["regime"]==regime and r["policy"]==policy]
            entry={"regime":regime,"policy":policy,"n":len(group)}
            for metric in ("absolute_error","duplicate_effects","duplicates_prevented","replay_delta","pending","dlq_rate","elapsed_ms","p95_delivery_us","peak_kib"):
                vals=[float(r[metric]) for r in group]
                entry[metric+"_mean"]=round(statistics.mean(vals),4)
                entry[metric+"_ci95_halfwidth"]=round(2.045*statistics.stdev(vals)/math.sqrt(len(vals)),4)
            summary.append(entry)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="440">','<rect width="100%" height="100%" fill="white"/>','<text x="30" y="35" font-size="20">Absolute effect error by regime, 30 seeds</text>']
    colors={"naive":"#C65353","inbox":"#2E8B57","inbox_no_retry":"#D49B32"}
    maxv=max(x["absolute_error_mean"] for x in summary) or 1
    for i,regime in enumerate(REGIMES):
        for j,policy in enumerate(POLICIES):
            item=next(x for x in summary if x["regime"]==regime and x["policy"]==policy)
            val=item["absolute_error_mean"]
            height=270*val/maxv
            x=100+280*i+65*j
            svg.append(f'<rect x="{x}" y="{360-height:.2f}" width="52" height="{height:.2f}" fill="{colors[policy]}"/>')
            svg.append(f'<text x="{x}" y="{350-height:.2f}" font-size="11">{val:.0f}</text>')
        svg.append(f'<text x="{150+280*i}" y="385" font-size="13">{regime}</text>')
    svg.append('<text x="140" y="420" font-size="12">Red: naive | Green: inbox | Amber: inbox without recovery</text>')
    svg.append('</svg>')
    (RESULTS/"error_by_regime.svg").write_text("\n".join(svg)+"\n",encoding="utf-8")
    report={"experiment":"event-inbox-replay-v1","runs":len(rows),"config":{"seeds":list(range(30)),"unique_events":120,"regimes":REGIMES,"policies":POLICIES,"invalid_rate":0.05,"conflict_rate":0.05},"environment":{"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,"os":platform.platform()},"wall_seconds":round(time.perf_counter()-t0,3),"summary":summary}
    (RESULTS/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"Benchmark: {len(rows)} runs; {report['wall_seconds']} s")
    for r in summary:
        print(r["regime"],r["policy"],"error",r["absolute_error_mean"],"replay",r["replay_delta_mean"],"p95_us",r["p95_delivery_us_mean"])

if __name__=="__main__":
    main()
