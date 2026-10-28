"""Exact finite-action audit; outcomes are known synthetic probabilities."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import platform
from statistics import median
import time
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.incentives import Action,audit,design,response


def save(path,rows):
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'config.json').read_text())
    actions=[Action(**a) for a in cfg['actions']]
    tracemalloc.start()
    tick=time.perf_counter()
    selected=design(actions,cfg['target'],cfg['bonus_rate'],cfg['menu'],cfg['required_margin'],cfg['outside_utility'])
    elapsed=time.perf_counter()-tick
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    baseline=response(actions,cfg['bonus_rate'],0)
    rows=[]
    for f in cfg['menu']:
        result=audit(actions,cfg['target'],cfg['bonus_rate'],f)
        actual=response(actions,cfg['bonus_rate'],f)
        rows.append({'deferred':f,'implemented':actual['name'],'ic_margin':result['ic_margin'],
                     'target_utility':result['target']['manager_utility'],'actual_principal_net':actual['net_profit'],
                     'actual_bonus':actual['expected_bonus']})
    save(root/'results'/'contracts.csv',rows)
    sensitivity=[]
    for failure in (.1,.3,.5):
        changed=[actions[0],replace(actions[1],failure_probability=failure)]
        try:
            result=design(changed,cfg['target'],cfg['bonus_rate'],cfg['menu'])
            sensitivity.append({'alternative_failure':failure,'feasible':True,'deferred':result['deferred'],'ic_margin':result['ic_margin']})
        except ValueError:
            sensitivity.append({'alternative_failure':failure,'feasible':False,'deferred':None,'ic_margin':None})
    save(root/'results'/'sensitivity.csv',sensitivity)
    scaling=[]
    for count in (2,20,200):
        extended=[actions[0]]+[replace(actions[1],name=f'alternative{i}') for i in range(count-1)]
        durations=[]
        for _ in range(5):
            start=time.perf_counter()
            result=design(extended,cfg['target'],cfg['bonus_rate'],cfg['menu'])
            durations.append(time.perf_counter()-start)
        assert result['deferred']==selected['deferred']
        scaling.append({'actions':count,'median_seconds':median(durations),'repetitions':5,'deferred':result['deferred']})
    save(root/'results'/'scaling.csv',scaling)
    omitted=Action('unmodeled',300,.01,0,-100,0)
    stress=response(actions+[omitted],cfg['bonus_rate'],selected['deferred'])
    summary={'selected':selected,'baseline_immediate':baseline,'baseline_no_contract_net_profit':0.0,
             'increment_vs_no_contract':selected['target']['net_profit'],'omitted_action_stress':stress,
             'analytic_minimum_for_margin':(15-10+1+cfg['required_margin'])/(7.5-.5),
             'seconds':elapsed,'python_peak_bytes':peak,'python':platform.python_version(),'platform':platform.platform()}
    (root/'results'/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert selected['deferred']==.9
    assert selected['ic_margin']>=cfg['required_margin']
    assert stress['name']!=cfg['target']
    plt.style.use('seaborn-v0_8-whitegrid')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    for a in actions:
        utilities=[audit([a],a.name,cfg['bonus_rate'],f)['target']['manager_utility'] for f in cfg['menu']]
        axes[0].plot(cfg['menu'],utilities,'o-',label=a.name)
    axes[0].axvline(.9,color='black',linestyle='--',label='Menú seleccionado')
    axes[0].set(xlabel='Fracción diferida contingente',ylabel='Utilidad esperada ejecutiva',title='El volumen puede premiar la acción adversa')
    axes[0].legend(fontsize=8)
    axes[1].plot(cfg['menu'],[r['actual_principal_net'] for r in rows],'s-',color='#176B87')
    axes[1].axhline(0,color='black',linestyle='--')
    axes[1].set(xlabel='Fracción diferida contingente',ylabel='Beneficio neto firma (sintético)',title='Respuesta del agente, no acción impuesta')
    fig.tight_layout()
    fig.savefig(root/'results'/'alignment.png',dpi=150)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
