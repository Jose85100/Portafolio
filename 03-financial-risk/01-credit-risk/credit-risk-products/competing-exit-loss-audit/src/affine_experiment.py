"""Deterministic matched-data numerical audit; no empirical calibration."""
import csv
import json
import math
import platform
import statistics
import time
import tracemalloc
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.affine import project_affine


def simpson(start: float, end: float, d: float, p: float, rho: float,
            dt: float, panels: int = 2048) -> float:
    """Independent direct integrand quadrature, not the closed-form implementation."""
    h = dt / panels
    def f(u: float) -> float:
        return .45 * d * (start*(1-u/dt)+end*u/dt)*math.exp(-(d+p+rho)*u)
    return h/3 * (f(0)+f(dt)+math.fsum(
        (4 if j % 2 else 2)*f(j*h) for j in range(1,panels)))


def main() -> None:
    rows = []
    for start,end in [(100.,20.),(20.,100.),(100.,100.),(100.,0.)]:
        for d,p,rho in [(.24,1.2,.06),(.01,0.,0.),(1.,3.,.2)]:
            for dt in [.1,1.,3.]:
                r = project_affine([dt],[d],[p],[start],[end],discount_force=rho)
                oracle = simpson(start,end,d,p,rho,dt)
                rows.append(dict(start=start,end=end,d=d,p=p,rho=rho,years=dt,
                                 **asdict(r),oracle=oracle,
                                 absolute_error=abs(r.exact_loss-oracle),
                                 midpoint_error=abs(r.midpoint_loss-oracle)))
    Path('results').mkdir(exist_ok=True)
    with open('results/affine.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader();writer.writerows(rows)
    anchor=project_affine([1.],[.24],[1.2],[100.],[20.])
    timings={}
    for name,fn in [('closed_form',lambda:project_affine([1.],[.24],[1.2],[100.],[20.])),
                    ('simpson2048',lambda:simpson(100.,20.,.24,1.2,.06,1.))]:
        samples=[]
        for _ in range(7):
            t=time.perf_counter()
            for _ in range(50): fn()
            samples.append((time.perf_counter()-t)/50)
        tracemalloc.start();fn();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        timings[name]={'median_seconds':statistics.median(samples),
                       'samples_seconds':samples,'peak_python_bytes':peak}
    convergence=[]
    for panels in [16,32,64,128,256,512,1024,2048]:
        estimate=simpson(100.,20.,.24,1.2,.06,1.,panels)
        convergence.append({'panels':panels,'estimate':estimate,'absolute_error':abs(estimate-anchor.exact_loss)})
    with open('results/affine_convergence.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(convergence[0]));writer.writeheader();writer.writerows(convergence)
    scaling=[]
    for count in [1,12,120,360]:
        edges=[i/count for i in range(count+1)]
        args=([1/count]*count,[.24]*count,[1.2]*count,[100-80*t for t in edges[:-1]],[100-80*t for t in edges[1:]])
        t=time.perf_counter();r=project_affine(*args);seconds=time.perf_counter()-t
        scaling.append({'intervals':count,'seconds_single_call':seconds,'loss':r.exact_loss,'partition_error':abs(r.exact_loss-anchor.exact_loss)})
    with open('results/affine_scaling.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(scaling[0]));writer.writeheader();writer.writerows(scaling)
    metrics={'anchor':asdict(anchor),'cases':len(rows),
             'max_abs_error_vs_simpson2048':max(float(r['absolute_error']) for r in rows),
             'timings':timings,'python':platform.python_version(),'hardware':platform.platform(),
             'data':'designed deterministic synthetic grid; no sampling uncertainty',
             'hypothesis':'max absolute error <1e-8 money versus direct Simpson2048; no worse than midpoint within1e-8',
             'passed':all(float(r['absolute_error'])<1e-8 and float(r['absolute_error'])<=float(r['midpoint_error'])+1e-8 for r in rows)}
    Path('results/affine_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    labels=['constant start','midpoint','affine exact','end exposure']
    axes[0].bar(labels,[anchor.constant_start_loss,anchor.midpoint_loss,anchor.exact_loss,anchor.endpoint_loss],color=['#999999','#0072B2','#009E73','#D55E00'])
    axes[0].tick_params(axis='x',rotation=20);axes[0].set_ylabel('Expected loss (money units)');axes[0].set_title('Synthetic amortization 100 → 20; 1 year')
    ends=[float(v) for v in range(0,201,5)]
    for method,label,style in [('exact_loss','exact','-'),('midpoint_loss','midpoint','--'),('endpoint_loss','end EAD',':')]:
        axes[1].plot(ends,[getattr(project_affine([1.],[.24],[1.2],[100.],[e]),method) for e in ends],style,label=label)
    axes[1].set_xlabel('End exposure (money units)');axes[1].set_ylabel('Expected loss (money units)');axes[1].set_title('Sign reversal under increasing exposure');axes[1].legend()
    fig.savefig('results/affine.png',dpi=150);plt.close(fig)
    print(json.dumps(metrics,indent=2))


if __name__=='__main__': main()
