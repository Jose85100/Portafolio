"""Exhaustive synthetic schedule audit and executable priority baseline."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import platform
import time
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.schedule import Job, exact, feasible, greedy


def save(path, rows):
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config.json').read_text())
    jobs=[Job(**{**j,'dependencies':tuple(j.get('dependencies',()))}) for j in cfg['jobs']]
    args=(cfg['budgets'],cfg['people_capacity'],cfg['discount_per_period'])
    tracemalloc.start()
    start=time.perf_counter()
    optimum=exact(jobs,*args)
    elapsed=time.perf_counter()-start
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    baseline=greedy(jobs,*args)
    assert feasible(jobs,optimum['starts'],args[0],args[1])
    assert optimum['npv'] >= baseline['npv']-1e-10
    rows=[]
    for policy,result in [('greedy',baseline),('exact',optimum)]:
        for j in jobs:
            if j.name in result['starts']:
                t=result['starts'][j.name]
                rows.append({'policy':policy,'job':j.name,'start':t,'end':t+j.duration,'cost':j.cost,'benefit':j.benefit,'people':j.people})
    save(root/'results'/'schedules.csv',rows)
    sensitivity=[]
    for people in (1,2,3):
        for horizon in (2,3,4,5):
            tick=time.perf_counter()
            result=exact(jobs,[8]*horizon,people,.1)
            sensitivity.append({'people':people,'horizon':horizon,'npv':result['npv'],'checked':result['checked'],'seconds':time.perf_counter()-tick})
    save(root/'results'/'sensitivity.csv',sensitivity)
    enabling = []
    for benefit in (14, 20, 30):
        changed = [replace(j, benefit=benefit) if j.name == 'analytics' else j for j in jobs]
        result = exact(changed, *args)
        reference = greedy(changed, *args)
        enabling.append({'analytics_benefit': benefit, 'exact_npv': result['npv'], 'greedy_npv': reference['npv'],
                         'increment': result['npv']-reference['npv'], 'exact_platform_start': result['starts'].get('platform', -1)})
    save(root/'results'/'enabling-value.csv', enabling)
    no_dependencies=[replace(j,dependencies=()) for j in jobs]
    relaxed=exact(no_dependencies,*args)
    summary={'exact':optimum,'baseline':baseline,'increment':optimum['npv']-baseline['npv'],
             'dependency_relaxation':relaxed,'relaxed_schedule_feasible_original':feasible(jobs,relaxed['starts'],args[0],args[1]),
             'seconds':elapsed,'python_peak_bytes':peak,'python':platform.python_version(),'platform':platform.platform()}
    (root/'results'/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),sharey=True)
    for ax,policy,result in zip(axes,['Greedy factible','Exacto'],[baseline,optimum]):
        for i,j in enumerate(jobs):
            if j.name in result['starts']:
                ax.barh(i,j.duration,left=result['starts'][j.name],color='#176B87' if policy=='Exacto' else '#A23B3B')
        ax.set(xlabel='Período (inicio y fin)',title=f'{policy}: NPV={result["npv"]:.3f}',xticks=range(5),xlim=(0,4))
        ax.set_yticks(range(len(jobs)),[j.name for j in jobs])
    fig.tight_layout()
    fig.savefig(root/'results'/'schedule.png',dpi=150)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
