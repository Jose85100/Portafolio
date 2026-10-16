"""Finite-language conformance audit; not a BPMN/Petri-net aligner."""
import csv
import json
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

PATHS = (
    ("intake","validate","manual_review","approve","settle","archive"),
    ("intake","validate","auto_check","approve","notify","archive"),
    ("intake","validate","manual_review","reject","archive"),
    ("intake","validate","auto_check","reject","archive"),
)
REGIMES = {"hybrid_heavy":48,"balanced":30,"local_heavy":12}
SEEDS = range(20261016,20261046)

def checked(trace):
    t = tuple(trace)
    if not t or any(not isinstance(a,str) or not a.strip() for a in t):
        raise ValueError("nonempty activity trace required")
    return t

def activity_set(trace):
    return all(a in {x for p in PATHS for x in p} for a in checked(trace))

def direct_follows(trace):
    t = checked(trace)
    pairs = {(a,b) for p in PATHS for a,b in zip(p,p[1:])}
    return t[0] in {p[0] for p in PATHS} and t[-1] in {p[-1] for p in PATHS} and all(
        x in pairs for x in zip(t,t[1:]))

def alignment(trace):
    """Unit-cost Levenshtein distance to finite approved language; O(K*n*m)."""
    t = checked(trace)
    best = None
    for p in PATHS:
        n,m = len(t),len(p)
        d = [[0]*(m+1) for _ in range(n+1)]
        for i in range(n+1): d[i][0] = i
        for j in range(m+1): d[0][j] = j
        for i in range(1,n+1):
            for j in range(1,m+1):
                d[i][j] = min(d[i-1][j-1]+(t[i-1]!=p[j-1]),d[i-1][j]+1,d[i][j-1]+1)
        if best is None or d[n][m] < best[0]: best = (d[n][m],p)
    return best

def sample(seed, hybrids):
    r = random.Random(seed)
    rows = [(r.choice(PATHS),0,"clean") for _ in range(60)]
    for _ in range(hybrids):
        suffix = "notify" if r.randrange(2) else "settle"
        prefix = "manual_review" if suffix == "notify" else "auto_check"
        rows.append((("intake","validate",prefix,"approve",suffix,"archive"),1,"hybrid"))
    for _ in range(60-hybrids):
        t = list(r.choice(PATHS))
        mode = r.choice(("missing","duplicate","unknown","swap"))
        if mode == "missing": t.remove("validate")
        elif mode == "duplicate": t.insert(2,"validate")
        elif mode == "unknown": t.insert(2,"unapproved_activity")
        else: t[1],t[2] = t[2],t[1]
        rows.append((tuple(t),1,"local"))
    r.shuffle(rows)
    assert len(rows)==120 and all(int(t not in PATHS)==y for t,y,_ in rows)
    return rows

def score(y,p):
    tp = sum(a==b==1 for a,b in zip(y,p))
    fp = sum(a==0 and b==1 for a,b in zip(y,p))
    fn = sum(a==1 and b==0 for a,b in zip(y,p))
    tn = sum(a==b==0 for a,b in zip(y,p))
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,precision=precision,recall=recall,
                f1=2*precision*recall/(precision+recall) if precision+recall else 0,
                accuracy=(tp+tn)/len(y))

def run():
    root = Path(__file__).resolve().parents[1]
    out = root/"results"
    out.mkdir(exist_ok=True)
    methods = {"activity_set":activity_set,"direct_follows":direct_follows,
               "alignment_tolerant":lambda t:alignment(t)[0]<=1,
               "alignment":lambda t:alignment(t)[0]==0}
    rows = []
    for regime,h in REGIMES.items():
        for seed in SEEDS:
            cases = sample(seed,h)
            traces = [t for t,_,_ in cases]
            truth = [y for _,y,_ in cases]
            for name,detector in methods.items():
                tracemalloc.start()
                start = time.perf_counter_ns()
                predicted = [int(not detector(t)) for t in traces]
                elapsed = time.perf_counter_ns()-start
                _,peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append(dict(regime=regime,seed=seed,method=name,**score(truth,predicted),
                                 total_ms=round(elapsed/1e6,6),peak_python_bytes=peak))
    with (out/"per_seed.csv").open("w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    summary = {}
    for regime in REGIMES:
        summary[regime] = {}
        for name in methods:
            v = [x for x in rows if x["regime"]==regime and x["method"]==name]
            recalls = [x["recall"] for x in v]
            summary[regime][name] = dict(
                recall_mean=statistics.mean(recalls),
                recall_95_normal_halfwidth=1.96*statistics.stdev(recalls)/math.sqrt(len(v)),
                f1_mean=statistics.mean(x["f1"] for x in v),
                missed_anomalies_total=sum(x["fn"] for x in v),
                median_batch_ms=statistics.median(x["total_ms"] for x in v),
                median_peak_python_bytes=statistics.median(x["peak_python_bytes"] for x in v))
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (out/"config.json").write_text(json.dumps({
        "seed_start":min(SEEDS),"seed_end":max(SEEDS),"regimes":REGIMES,
        "cases_per_dataset":120,"datasets":90,"evaluations":len(rows),
        "python":sys.version.split()[0],"platform":platform.platform(),
        "machine":platform.machine(),"data":"synthetic"},indent=2)+"\n")
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="490">',
         '<rect width="900" height="490" fill="white"/>',
         '<text x="25" y="30" font-family="sans-serif" font-size="18">Synthetic anomaly recall by regime</text>']
    colors={"activity_set":"#94a3b8","direct_follows":"#64748b",
            "alignment_tolerant":"#d97706","alignment":"#2563eb"}
    for k,(regime,group) in enumerate(summary.items()):
        x=40+290*k
        svg.append(f'<text x="{x}" y="80" font-family="sans-serif">{regime}</text>')
        for j,(method,vals) in enumerate(group.items()):
            y=115+82*j
            recall=vals["recall_mean"]
            svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="12">{method}: {recall:.3f}</text>')
            svg.append(f'<rect x="{x}" y="{y+9}" width="{170*recall:.1f}" height="22" fill="{colors[method]}"/>')
    svg.append('<text x="25" y="470" font-family="sans-serif" font-size="11">Truth shares the approved paths; no external validity claim.</text></svg>')
    (out/"recall.svg").write_text("\n".join(svg)+"\n")
    # Notebook with actually executed output, not a placeholder.
    import contextlib,io
    cells=[
        "from src.engine import PATHS,alignment,direct_follows\nprint('Approved paths:',len(PATHS))",
        "t=('intake','validate','manual_review','approve','notify','archive')\nprint('Pairwise:',direct_follows(t),'global edit:',alignment(t)[0])",
        "import json\ns=json.load(open('results/summary.json'))\nfor k,v in s.items():print(k,round(v['direct_follows']['recall_mean'],3),round(v['alignment']['recall_mean'],3))",
        "print('Synthetic labels share the finite path reference; not external validation.')"]
    ns={}
    nb={"nbformat":4,"nbformat_minor":5,"metadata":{
        "kernelspec":{"name":"python3","display_name":"Python 3","language":"python"},
        "language_info":{"name":"python","version":sys.version.split()[0]}},"cells":[]}
    for i,code in enumerate(cells,1):
        buf=io.StringIO()
        with contextlib.redirect_stdout(buf):exec(compile(code,f"cell_{i}","exec"),ns)
        nb["cells"].append({"cell_type":"code","id":f"executed-{i}","execution_count":i,
                            "metadata":{},"source":code.splitlines(keepends=True),
                            "outputs":[{"output_type":"stream","name":"stdout",
                                        "text":buf.getvalue().splitlines(keepends=True)}]})
    (root/"notebook.ipynb").write_text(json.dumps(nb,indent=1)+"\n")
    print(json.dumps({"evaluations":len(rows),"cases":10800,
          "recall":{r:{m:round(v["recall_mean"],3) for m,v in d.items()}
                    for r,d in summary.items()}},indent=2))

if __name__=="__main__":run()
