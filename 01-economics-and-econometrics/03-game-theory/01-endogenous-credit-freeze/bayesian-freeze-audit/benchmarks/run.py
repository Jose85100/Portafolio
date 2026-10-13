"""Equilibrium completeness, selection bounds, rational oracle, cost and sensitivity."""
import csv
from fractions import Fraction
from dataclasses import asdict
import hashlib
import json
from itertools import product
import platform
from pathlib import Path
import sys
import time
import tracemalloc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.game import Game, PROFILES, equilibria, exact_equilibria, gain, iterate, outcomes, regret
ROOT=Path(__file__).resolve().parents[1]

def csv_file(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    g=Game(); eq=equilibria(g)
    main_rows=[dict(profile=str(p),regret=regret(g,p),**outcomes(g,p)) for p in eq]
    for name,start in [('baseline_bottom',((0,0),(0,0))),('baseline_top',((1,1),(1,1)))]:
        found,steps=iterate(g,start)
        assert found is not None
        main_rows.append(dict(profile=name,regret=regret(g,found),**outcomes(g,found)))
    csv_file('main.csv',main_rows)
    grid=[]
    for q,c,a in product((.6,.8,.95),np.linspace(0,1.6,41),np.linspace(0,1.2,31)):
        game=Game(accuracy=q,cost=float(c),complementarity=float(a));es=equilibria(game)
        bottom,steps=iterate(game)
        bounds=[outcomes(game,p)['freeze_given_good'] for p in es]
        grid.append(dict(q=q,cost=c,alpha=a,equilibria=len(es),baseline_found=int(bottom is not None),
             baseline_steps=steps,missed=max(0,len(es)-int(bottom is not None)),
             freeze_min=min(bounds),freeze_max=max(bounds)))
    csv_file('grid.csv',grid)
    # Precision: rational independently summed payoffs versus analytic float formula.
    rng=np.random.default_rng(20261013); oracle=[]
    for i in range(100):
        game=Game(prior=int(rng.integers(1,10))/10,accuracy=int(rng.integers(5,11))/10,
                  cost=int(rng.integers(0,21))/10,complementarity=int(rng.integers(0,16))/10)
        es=equilibria(game); exact=exact_equilibria(game)
        assert es==exact
        pi,q,c,a=[Fraction(str(v)) for v in (game.prior,game.accuracy,game.cost,game.complementarity)]
        errors=[]
        for signal,other in product((0,1),((0,0),(0,1),(1,0),(1,1))):
            numerator=Fraction(0);denominator=Fraction(0)
            for theta,t in product((0,1),repeat=2):
                prob=(pi if theta else 1-pi)*(q if signal==theta else 1-q)*(q if t==theta else 1-q)
                numerator+=prob*(theta+a*other[t]-c);denominator+=prob
            errors.append(abs(gain(game,signal,other)-float(numerator/denominator)))
        oracle.append(dict(case=i,**asdict(game),float_count=len(es),rational_count=len(exact),
                           mismatch=int(es!=exact),max_abs_gain_error=max(errors)))
    csv_file('oracle.csv',oracle)
    costs=[]
    for n in (100,1000,5000):
        games=[Game(cost=.2+1.2*(i%37)/36,complementarity=1.2*(i%31)/30) for i in range(n)]
        for name,solver in [('enumeration',equilibria),('single_start',iterate)]:
            for rep in range(3):
                tracemalloc.start();start=time.perf_counter()
                for game in games: solver(game)
                seconds=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
                costs.append(dict(n=n,method=name,repeat=rep,seconds=seconds,peak_python_bytes=peak))
    # Direct rational oracle cost on same first 100 games; no equivalent scalability claim.
    for rep in range(3):
        tracemalloc.start();start=time.perf_counter()
        for game in games[:100]: exact_equilibria(game)
        seconds=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        costs.append(dict(n=100,method='rational_oracle',repeat=rep,seconds=seconds,peak_python_bytes=peak))
    csv_file('costs.csv',costs)
    tolerances=[]
    for tol in (0.,1e-14,1e-12,1e-8):
        for game in (g,Game(accuracy=.5,cost=.5,complementarity=0)):
            tolerances.append(dict(tolerance=tol,accuracy=game.accuracy,cost=game.cost,alpha=game.complementarity,count=len(equilibria(game,tol))))
    csv_file('tolerance.csv',tolerances)
    summary=dict(main_equilibria=len(eq),baseline_equilibria=1,grid_games=len(grid),
         multiple_games=sum(r['equilibria']>1 for r in grid),max_equilibria=max(r['equilibria'] for r in grid),max_abs_gain_error=max(r['max_abs_gain_error'] for r in oracle),
         oracle_mismatches=sum(r['mismatch'] for r in oracle),
         no_complementarity_count=len(equilibria(Game(complementarity=0))),
         uninformative_tie_count=len(equilibria(Game(accuracy=.5,cost=.5,complementarity=0))))
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2))
    fig,ax=plt.subplots(figsize=(7,5));selected=[r for r in grid if r['q']==.8]
    image=np.array([r['equilibria'] for r in selected]).reshape(41,31)
    im=ax.imshow(image,origin='lower',extent=[0,1.2,0,1.6],aspect='auto',vmin=1,vmax=4)
    ax.set(xlabel='Complementarity alpha',ylabel='Cost c',title='Pure Bayesian equilibrium count, q=0.8 (finite game)')
    fig.colorbar(im,ax=ax,label='Equilibria');fig.tight_layout();fig.savefig(ROOT/'results/equilibria.png',dpi=150);plt.close(fig)
    meta=dict(config=asdict(g),seed=20261013,python=sys.version,platform=platform.platform(),
       cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown'),
       base_commit='75423ac53aab6ed8f6d28da478307c1ce04dead1',memory='tracemalloc allocations, excludes native allocations and input games',
       profile_space=len(PROFILES),date='2026-10-13',hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'results').glob('*.csv')})
    (ROOT/'results/metadata.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
