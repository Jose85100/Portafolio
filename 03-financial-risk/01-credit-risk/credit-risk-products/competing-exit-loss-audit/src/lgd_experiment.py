"""Matched analytic/quadrature audit of deterministic affine EAD x LGD paths."""
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

from src.affine_lgd import project_loss_path


def simpson(e0: float,e1: float,l0: float,l1: float,d: float,p: float,r: float,
            dt: float,panels: int=4096) -> float:
    """Independent direct integral on one interval; no moment formulas reused."""
    def f(v: float) -> float:
        return d*dt*((1-v)*e0+v*e1)*((1-v)*l0+v*l1)*math.exp(-(d+p+r)*dt*v)
    return (f(0.)+f(1.)+math.fsum((4 if j%2 else 2)*f(j/panels)
        for j in range(1,panels)))/(3*panels)


def main() -> None:
    rows=[]
    for e0,e1 in [(100.,20.),(20.,100.),(100.,100.)]:
        for l0,l1 in [(.8,.2),(.2,.8),(.45,.45)]:
            for d,p,r,dt in [(.24,1.2,.06,1.),(.01,0.,0.,.1),(1.,3.,.2,3.)]:
                result=project_loss_path([dt],[d],[p],[e0],[e1],[l0],[l1],[r])
                oracle=simpson(e0,e1,l0,l1,d,p,r,dt)
                rows.append({'ead_start':e0,'ead_end':e1,'lgd_start':l0,'lgd_end':l1,
                    'default_hazard':d,'prepay_hazard':p,'discount_force':r,'years':dt,
                    **asdict(result),'simpson4096':oracle,'absolute_error':abs(result.exact_loss-oracle)})
    anchor=project_loss_path([1.],[.24],[1.2],[100.],[20.],[.8],[.2],[.06])
    convergence=[]
    for panels in [8,16,32,64,128,256,512,1024,4096]:
        value=simpson(100.,20.,.8,.2,.24,1.2,.06,1.,panels)
        convergence.append({'panels':panels,'loss':value,'absolute_error':abs(value-anchor.exact_loss)})
    scaling=[]
    for n in [1,12,120,360]:
        e=[100-80*j/n for j in range(n+1)];l=[.8-.6*j/n for j in range(n+1)]
        start=time.perf_counter();out=project_loss_path([1/n]*n,[.24]*n,[1.2]*n,e[:-1],e[1:],l[:-1],l[1:],[.06]*n);seconds=time.perf_counter()-start
        scaling.append({'intervals':n,'seconds_single_call':seconds,'partition_error':abs(out.exact_loss-anchor.exact_loss)})
    Path('results').mkdir(exist_ok=True)
    for name,data in [('lgd_grid',rows),('lgd_convergence',convergence),('lgd_scaling',scaling)]:
        with open('results/'+name+'.csv','w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    timings={}
    for name,fn in [('closed_form',lambda:project_loss_path([1.],[.24],[1.2],[100.],[20.],[.8],[.2],[.06])),
                    ('simpson4096',lambda:simpson(100.,20.,.8,.2,.24,1.2,.06,1.))]:
        samples=[]
        for _ in range(7):
            start=time.perf_counter()
            for _ in range(25):fn()
            samples.append((time.perf_counter()-start)/25)
        tracemalloc.start();fn();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        timings[name]={'median_seconds':statistics.median(samples),'samples_seconds':samples,'peak_python_bytes':peak}
    metrics={'anchor':asdict(anchor),'cases':len(rows),'max_absolute_error':max(float(row['absolute_error']) for row in rows),
        'max_partition_error':max(float(row['partition_error']) for row in scaling),
        'hypothesis':'absolute error<1e-8 money vs same-DGP Simpson4096; constant LGD recovers prior engine',
        'passed':all(float(row['absolute_error'])<1e-8 for row in rows),'timings':timings,
        'python':platform.python_version(),'hardware':platform.platform(),
        'interpretation':'temporal covariance under deterministic default-time weighting, not estimated stochastic dependence'}
    Path('results/lgd_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    ends=[j/50 for j in range(51)]
    errors=[]
    for end in ends:
        value=project_loss_path([1.],[.24],[1.2],[100.],[20.],[.5],[end],[.06])
        errors.append(value.exact_loss-value.product_of_means_loss)
    axes[0].plot(ends,errors);axes[0].axhline(0,color='black',linestyle='--');axes[0].axvline(.5,color='black',linestyle=':')
    axes[0].set(xlabel='Terminal LGD (fraction)',ylabel='Exact minus product of means (money)',title='Synthetic EAD100→20; initial LGD .5\n1 year; d=.24, p=1.2, r=.06')
    axes[1].loglog([int(row['panels']) for row in convergence],[float(row['absolute_error']) for row in convergence],'o-')
    axes[1].set(xlabel='Simpson panels',ylabel='Absolute error (money)',title='Matched affine EAD/LGD: quadrature convergence')
    fig.savefig('results/lgd.png',dpi=150);plt.close(fig)
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':main()
