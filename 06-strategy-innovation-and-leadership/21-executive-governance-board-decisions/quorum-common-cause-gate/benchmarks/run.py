"""Tiny exact committee availability audit under a common-cause mixture."""
import csv
import json
from pathlib import Path
import platform
from statistics import median
import time
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.quorum import Regime,add_standbys,choose,enumerate_states,exact,independent_marginals


def save(path,rows):
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config.json').read_text())
    regimes=[Regime(r['name'],r['weight'],tuple(r['attendance'])) for r in cfg['regimes']]
    args=(regimes,cfg['quorum'],tuple(cfg['mandatory']),cfg['standby_menu'],cfg['standby_attendance'],cfg['unit_standby_cost'],cfg['target'])
    tracemalloc.start()
    tick=time.perf_counter()
    selected=choose(*args)
    elapsed=time.perf_counter()-tick
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    baseline=choose(*args,independent=True)
    actual_baseline=exact(add_standbys(regimes,baseline['standbys'],.9),3,(0,))['available']
    rows=[]
    raw=[]
    for count in cfg['standby_menu']:
        expanded=add_standbys(regimes,count,.9)
        measured=exact(expanded,3,(0,))
        approximation=independent_marginals(expanded,3,(0,))
        rows.append({'standbys':count,'cost':count,'exact_availability':measured['available'],'independent_marginal':approximation['available'],'states':measured['states']})
        raw.extend({'standbys':count,**r} for r in enumerate_states(expanded,3,(0,)))
    save(root/'results'/'plans.csv',rows)
    save(root/'results'/'state_masses.csv',raw)
    sensitivity=[]
    for disruption in (.1,.2,.4,.8):
        changed=[Regime('normal',1-disruption,regimes[0].attendance),Regime('shock',disruption,regimes[1].attendance)]
        try:
            result=choose(changed,3,(0,),[0,1,2],.9,1,.85)
            sensitivity.append({'disruption_weight':disruption,'feasible':True,**result})
        except ValueError:
            sensitivity.append({'disruption_weight':disruption,'feasible':False,'standbys':None,'cost':None,'availability':None})
    save(root/'results'/'sensitivity.csv',sensitivity)
    scaling=[]
    for n in (4,6,8):
        expanded=add_standbys(regimes,n-4,.9)
        durations=[]
        for _ in range(5):
            start=time.perf_counter()
            result=exact(expanded,3,(0,))
            durations.append(time.perf_counter()-start)
        scaling.append({'members':n,'states':result['states'],'median_seconds':median(durations),'repetitions':5})
    save(root/'results'/'scaling.csv',scaling)
    summary={'selected_exact':selected,'baseline_independent':baseline,'actual_baseline_availability':actual_baseline,
             'independence_error':baseline['availability']-actual_baseline,'seconds':elapsed,'python_peak_bytes':peak,
             'python':platform.python_version(),'platform':platform.platform()}
    (root/'results'/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert baseline['availability']>=cfg['target']>actual_baseline
    assert selected['availability']>=cfg['target']
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.plot([r['standbys'] for r in rows],[r['exact_availability'] for r in rows],'o-',color='#176B87',label='Mezcla exacta de regímenes')
    ax.plot([r['standbys'] for r in rows],[r['independent_marginal'] for r in rows],'s--',color='#A23B3B',label='Independencia de marginales')
    ax.axhline(.85,color='black',linestyle=':',label='Meta sintética 0,85')
    ax.set(xlabel='Participantes de reserva autorizados',ylabel='Probabilidad de poder formar quórum',title='La asistencia marginal oculta una causa común',xticks=[0,1,2],ylim=(.7,1))
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(root/'results'/'quorum.png',dpi=150)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
