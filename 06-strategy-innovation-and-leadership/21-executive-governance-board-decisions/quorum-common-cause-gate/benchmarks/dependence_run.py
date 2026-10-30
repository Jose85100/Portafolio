"""Cumulative Oct30 experiment: reserve dependence ambiguity after Oct29."""
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
from src.reserve_ambiguity import ReservePlan,bounds,choose_plan,coupling,nominal_existing_engine,symmetric_threshold


def save(path,rows):
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config_dependence.json').read_text())
    plans=[ReservePlan(**p) for p in cfg['plans']]
    kw={'target':cfg['target'],'shock':cfg['shock'],'risk':cfg['risk_role_attendance']}
    tracemalloc.start()
    tick=time.perf_counter()
    nominal=choose_plan(plans,robust=False,**kw)
    robust=choose_plan(plans,**kw)
    elapsed=time.perf_counter()-tick
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    rows=[]
    for plan in plans:
        b=bounds(plan,kw['shock'],kw['risk'])
        recovered=nominal_existing_engine(plan,kw['shock'],kw['risk'])
        assert abs(recovered-b['nominal_availability'])<1e-12
        rows.append({'name':plan.name,'q1':plan.q1,'q2':plan.q2,'cost':plan.cost,**b,'oct29_engine_nominal':recovered})
    save(root/'results'/'dependence_plans.csv',rows)
    couplings=[]
    p=plans[0]
    b=bounds(p)
    for label,joint in [('lower',b['lower_joint']),('independent',b['independent_joint']),('upper_positive',b['upper_joint'])]:
        for state,mass in zip(('00','01','10','11'),coupling(p,joint)):
            couplings.append({'case':label,'state':state,'probability':mass,'q1':p.q1,'q2':p.q2})
    save(root/'results'/'reserve_couplings.csv',couplings)
    sensitivity=[]
    for i in range(11):
        q=i/10
        p=ReservePlan('sweep',q,q,1)
        sensitivity.append({'q':q,**bounds(p)})
    save(root/'results'/'dependence_sensitivity.csv',sensitivity)
    scaling=[]
    for count in (3,30,300):
        menu=[ReservePlan(f'plan{i}',plans[i%3].q1,plans[i%3].q2,plans[i%3].cost) for i in range(count)]
        timings=[]
        for _ in range(5):
            start=time.perf_counter()
            answer=choose_plan(menu,**kw)
            timings.append(time.perf_counter()-start)
        assert abs(answer['lower_availability']-robust['lower_availability'])<1e-12
        scaling.append({'plans':count,'median_seconds':median(timings),'repetitions':5})
    save(root/'results'/'dependence_scaling.csv',scaling)
    critical=symmetric_threshold(**kw)
    summary={'nominal_choice':nominal,'robust_choice':robust,'critical_nominal_q':critical[0],'critical_robust_q':critical[1],
             'original29_q09_bounds':bounds(ReservePlan('original29',.9,.9,2)),
             'seconds':elapsed,'python_peak_bytes':peak,'python':platform.python_version(),'platform':platform.platform()}
    (root/'results'/'dependence_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert nominal['nominal_availability']>=cfg['target']>nominal['lower_availability']
    assert robust['lower_availability']>=cfg['target']
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,ax=plt.subplots(figsize=(8,4.5))
    q=[r['q'] for r in sensitivity]
    ax.fill_between(q,[r['lower_availability'] for r in sensitivity],[r['upper_availability'] for r in sensitivity],alpha=.18,color='#176B87',label='Banda sharp sobre acoplamientos')
    ax.plot(q,[r['nominal_availability'] for r in sensitivity],'o-',color='#176B87',label='Reservas condicionalmente independientes')
    ax.plot(q,[r['lower_availability'] for r in sensitivity],'s--',color='#A23B3B',label='Peor dependencia factible')
    ax.axhline(.85,color='black',linestyle=':',label='Meta0,85')
    ax.set(xlabel='Asistencia marginal de cada reserva durante disrupción',ylabel='Disponibilidad del mismo quórum3 + rol obligatorio',title='El supuesto pendiente del29: dependencia entre reservas',ylim=(.73,.97))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(root/'results'/'dependence.png',dpi=150)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
