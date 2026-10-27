"""Scenario-based CFO trigger audit with debt/cash reconciliation."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import platform
import time
from statistics import median
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.funding import Facility,choose,score


def save(path,rows):
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config.json').read_text())
    facility=Facility(**cfg['facility'])
    flows,weights=cfg['flows'],cfg['weights']
    tracemalloc.start()
    tick=time.perf_counter()
    selected=choose(flows,weights,cfg['thresholds'],facility,cfg['max_breach'])
    elapsed=time.perf_counter()-tick
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    baseline=score(flows,weights,2,facility)
    rows=[]
    for h in cfg['thresholds']:
        r=score(flows,weights,h,facility)
        rows.append({k:v for k,v in r.items() if k!='outcomes'})
    save(root/'results'/'thresholds.csv',rows)
    trajectories=[]
    for policy,result in [('reactive2',baseline),('selected',selected)]:
        for name,outcome in zip(cfg['names'],result['outcomes']):
            for t,(cash,debt) in enumerate(zip(outcome['cash'],outcome['debt'])):
                trajectories.append({'policy':policy,'scenario':name,'period':t,'cash':cash,'debt':debt,'request_period':outcome['request_period'],'funding_period':outcome['funding_period'],'first_breach':outcome['first_breach'],'costs_total':outcome['costs'],'reconciliation_error':outcome['reconciliation_error']})
    save(root/'results'/'trajectories.csv',trajectories)
    sensitivity=[]
    for lead in (0,1,2,3,4):
        try:
            r=choose(flows,weights,cfg['thresholds'],replace(facility,lead=lead),cfg['max_breach'])
            sensitivity.append({'lead':lead,'threshold':r['threshold'],'breach_probability':r['breach_probability'],'expected_cost':r['expected_cost'],'feasible':True})
        except ValueError:
            sensitivity.append({'lead':lead,'threshold':None,'breach_probability':None,'expected_cost':None,'feasible':False})
    save(root/'results'/'lead-sensitivity.csv',sensitivity)
    scaling=[]
    for copies in (1,10,100):
        expanded=flows*copies
        probabilities=[w/copies for _ in range(copies) for w in weights]
        timings=[]
        for _ in range(5):
            tick=time.perf_counter()
            result=choose(expanded,probabilities,cfg['thresholds'],facility,cfg['max_breach'])
            timings.append(time.perf_counter()-tick)
        assert result['threshold']==selected['threshold']
        assert abs(result['expected_cost']-selected['expected_cost'])<1e-10
        scaling.append({'scenarios':len(expanded),'repetitions':5,'median_seconds':median(timings),'threshold':result['threshold'],'expected_cost':result['expected_cost']})
    save(root/'results'/'scaling.csv',scaling)
    # Structural stress outside design scenario set: no safety claim transfers.
    stress=score([[-4,-4,-4,-4,-4]],[1],selected['threshold'],facility)
    summary={'selected':selected,'baseline_reactive2':baseline,'out_of_design_stress':stress,
             'seconds':elapsed,'python_peak_bytes':peak,'python':platform.python_version(),'platform':platform.platform()}
    (root/'results'/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert selected['breach_probability']<=cfg['max_breach']
    assert selected['breach_probability']<baseline['breach_probability']
    assert all(r['reconciliation_error']<1e-10 for r in selected['outcomes'])
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),sharey=True)
    for ax,title,result in zip(axes,['Reactivo: umbral2','Seleccionado: umbral6'],[baseline,selected]):
        for name,outcome in zip(cfg['names'],result['outcomes']):
            ax.plot(range(5),outcome['cash'],'o-',label=name)
        ax.axhline(0,color='black',linestyle='--')
        ax.set(xlabel='Período',ylabel='Caja (unidades sintéticas)',title=title,xticks=range(5))
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(root/'results'/'funding.png',dpi=150)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('selected','baseline_reactive2','out_of_design_stress')},indent=2))
    print('selected',selected['threshold'],selected['breach_probability'],selected['expected_cost'])
    print('baseline',baseline['breach_probability'],baseline['expected_cost'])


if __name__=='__main__':
    main()
