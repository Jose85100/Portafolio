"""Designed payment-event audit; semantically matched quadrature baselines."""
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

from src.term_structure import project_term_structure


def quadrature(dt: list[float], d: list[float], p: list[float], e: list[float],
               r: list[float], panels: int) -> float:
    """Independent midpoint rule on EACH constant-EAD event interval."""
    survival=discount=1.
    terms=[]
    for length,hd,hp,exposure,rate in zip(dt,d,p,e,r):
        h=length/panels
        terms.append(survival*discount*.45*hd*exposure*h*math.fsum(
            math.exp(-(hd+hp+rate)*(j+.5)*h) for j in range(panels)))
        survival*=math.exp(-(hd+hp)*length)
        discount*=math.exp(-rate*length)
    return math.fsum(terms)


def main() -> None:
    dt=[.13,.37,.5];d=[.24]*3;p=[1.2]*3;r=[.02,.08,.16]
    e=[100.,80.,20.]
    anchor=project_term_structure(dt,d,p,e,e,r)
    rows=[]
    for prepay in [0.,.5,1.2,3.]:
        for shift in [0.,.05,.2]:
            for payment in [0.,40.,80.]:
                exposure=[100.,100.-payment/2,100.-payment]
                rates=[v+shift for v in r]
                exact=project_term_structure(dt,d,[prepay]*3,exposure,exposure,rates)
                oracle=quadrature(dt,d,[prepay]*3,exposure,rates,4096)
                rows.append({'prepay':prepay,'rate_shift':shift,'total_payment':payment,
                             'exact':exact.exact_loss,'midpoint4096':oracle,
                             'absolute_error':abs(exact.exact_loss-oracle)})
    scaling=[]
    for panels in [1,4,16,64,256,1024,4096]:
        value=quadrature(dt,d,p,e,r,panels)
        scaling.append({'panels_per_event_interval':panels,'loss':value,
                        'absolute_error':abs(value-anchor.exact_loss)})
    Path('results').mkdir(exist_ok=True)
    for name,data in [('term_grid',rows),('term_convergence',scaling)]:
        with open('results/'+name+'.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    smooth=project_term_structure([.5,.5],[.24]*2,[1.2]*2,[100.,60.],[60.,20.],[.06]*2)
    discrete=project_term_structure([.5,.5],[.24]*2,[1.2]*2,[100.,20.],[100.,20.],[.06]*2)
    times={}
    for name,fn in [('closed_form',lambda:project_term_structure(dt,d,p,e,e,r)),
                    ('midpoint4096',lambda:quadrature(dt,d,p,e,r,4096))]:
        samples=[]
        for _ in range(7):
            start=time.perf_counter()
            for _ in range(25):fn()
            samples.append((time.perf_counter()-start)/25)
        tracemalloc.start();fn();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        times[name]={'median_seconds':statistics.median(samples),'samples_seconds':samples,'peak_python_bytes':peak}
    size_rows=[]
    for factor in [1,4,40,120]:
        lengths=[length/factor for length in dt for _ in range(factor)]
        hd=[v for v in d for _ in range(factor)]
        hp=[v for v in p for _ in range(factor)]
        exposure=[v for v in e for _ in range(factor)]
        rates=[v for v in r for _ in range(factor)]
        start=time.perf_counter();value=project_term_structure(lengths,hd,hp,exposure,exposure,rates);seconds=time.perf_counter()-start
        size_rows.append({'intervals':len(lengths),'seconds_single_call':seconds,'partition_error':abs(value.exact_loss-anchor.exact_loss)})
    with open('results/term_scaling.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(size_rows[0]));writer.writeheader();writer.writerows(size_rows)
    metrics={'anchor':asdict(anchor),'discrete_midyear_payment':discrete.exact_loss,
             'smooth_same_endpoints':smooth.exact_loss,'semantic_difference':discrete.exact_loss-smooth.exact_loss,
             'cases':len(rows),'max_abs_error':max(float(x['absolute_error']) for x in rows),
             'hypothesis':'max abs error <1e-6 money vs midpoint4096 on same event-DGP',
             'passed':max(float(x['absolute_error']) for x in rows)<1e-6,'timings':times,
             'python':platform.python_version(),'hardware':platform.platform()}
    Path('results/term_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    grid=[j/200 for j in range(201)]
    ax[0].step([0,.5,1],[100,20,20],where='post',label='Discrete payment at .5 year')
    ax[0].plot(grid,[100-80*t for t in grid],'--',label='Continuous amortization')
    ax[0].set(xlabel='Time (years)',ylabel='Conditional EAD (money units)',title='Different contracts: same endpoints');ax[0].legend(fontsize=8)
    ax[1].loglog([int(x['panels_per_event_interval']) for x in scaling],[float(x['absolute_error']) for x in scaling],'o-')
    ax[1].set(xlabel='Midpoint panels per event interval',ylabel='Absolute loss error (money units)',title='Matched contract: numerical convergence')
    fig.savefig('results/term.png',dpi=150);plt.close(fig)
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':main()
