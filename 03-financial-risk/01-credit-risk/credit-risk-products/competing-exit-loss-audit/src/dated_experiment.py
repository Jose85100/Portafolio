"""Executable date/unit/provenance adapter with explicitly synthetic inputs."""
import csv
import json
import platform
import statistics
import time
import tracemalloc
from dataclasses import asdict, replace
from datetime import date, datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.dated_contract import (
    Basis,
    DatedInterval,
    SourceStamp,
    convert_rate,
    project_dated,
)
from src.term_structure import project_term_structure


def load_fixture(path: Path) -> tuple[list[DatedInterval],list[SourceStamp],datetime,Basis]:
    raw=json.loads(path.read_text())
    if raw['synthetic'] is not True:raise ValueError('this benchmark requires synthetic fixture')
    intervals=[DatedInterval(date.fromisoformat(i['start']),date.fromisoformat(i['end']),
                i['default_hazard'],i['prepay_hazard'],i['ead_start'],i['ead_end'],i['discount_force']) for i in raw['intervals']]
    sources=[SourceStamp(s['role'],s['identifier'],s['uri'],datetime.fromisoformat(s['available_at'])) for s in raw['sources']]
    return intervals,sources,datetime.fromisoformat(raw['valuation_at']),raw['basis']


def main() -> None:
    items,sources,valuation,basis=load_fixture(Path('benchmarks/dated_fixture.json'))
    anchor=project_dated(items,sources,valuation,basis)
    rows=[]
    for month in [1,2,6,12]:
        for year in [2023,2024,2025]:
            for days in [30,365,366]:
                start=date(year,month,1);end=start+timedelta(days=days)
                stamp=valuation.replace(year=year,month=month,day=1)
                source=[replace(s,available_at=stamp) for s in sources]
                interval=DatedInterval(start,end,.24,1.2,100.,20.,.06)
                a=project_dated([interval],source,stamp,'ACT/365F')
                b=project_dated([replace(interval,default_hazard=convert_rate(.24,'ACT/365F','ACT/360'),
                    prepay_hazard=convert_rate(1.2,'ACT/365F','ACT/360'),
                    discount_force=convert_rate(.06,'ACT/365F','ACT/360'))],source,stamp,'ACT/360')
                naive=project_dated([interval],source,stamp,'ACT/360')
                rows.append({'start':str(start),'days':days,'act365_loss':a.exact_loss,
                             'converted360_loss':b.exact_loss,'naive360_loss':naive.exact_loss,
                             'unit_invariance_error':abs(a.exact_loss-b.exact_loss)})
    audits=[]
    for shift in [-24.,-1.,0.,.001,1.,24.]:
        changed=[replace(sources[0],available_at=valuation+timedelta(hours=shift)),*sources[1:]]
        try:project_dated(items,changed,valuation,basis);accepted=True
        except ValueError:accepted=False
        audits.append({'hours_after_valuation':shift,'accepted':accepted,'expected_acceptance':shift<=0})
    for name,data in [('dated_grid',rows),('dated_availability',audits)]:
        with open('results/'+name+'.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    dt=[(i.end-i.start).days/365 for i in items]
    direct=lambda:project_term_structure(dt,[i.default_hazard for i in items],[i.prepay_hazard for i in items],
        [i.ead_start for i in items],[i.ead_end for i in items],[i.discount_force for i in items])
    times={}
    for name,fn in [('dated_validated',lambda:project_dated(items,sources,valuation,basis)),('prevalidated_numeric',direct)]:
        samples=[]
        for _ in range(7):
            start_time=time.perf_counter()
            for _ in range(100):fn()
            samples.append((time.perf_counter()-start_time)/100)
        tracemalloc.start();fn();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        times[name]={'median_seconds':statistics.median(samples),'samples_seconds':samples,'peak_python_bytes':peak}
    scaling=[]
    for n in [1,12,120,360]:
        base=items[0].start
        seq=[replace(items[0],start=base+timedelta(days=k),end=base+timedelta(days=k+1)) for k in range(n)]
        start_time=time.perf_counter();value=project_dated(seq,sources,valuation,basis);seconds=time.perf_counter()-start_time
        scaling.append({'intervals':n,'seconds_single_call':seconds,'loss':value.exact_loss})
    with open('results/dated_scaling.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(scaling[0]));w.writeheader();w.writerows(scaling)
    metrics={'anchor':asdict(anchor),'calendar_days':[2,364],'total_days':366,
        'max_unit_invariance_error':max(float(x['unit_invariance_error']) for x in rows),
        'direct_numeric_error':abs(anchor.exact_loss-direct().exact_loss),
        'naive_anchor_360_loss':project_dated(items,sources,valuation,'ACT/360').exact_loss,
        'availability_cases':len(audits),'availability_correct':sum(a['accepted']==a['expected_acceptance'] for a in audits),
        'passed':all(float(x['unit_invariance_error'])<1e-12 for x in rows) and all(a['accepted']==a['expected_acceptance'] for a in audits),
        'timings':times,'python':platform.python_version(),'hardware':platform.platform()}
    Path('results/dated_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    row=rows[0]
    ax[0].bar(['ACT/365F','ACT/360 converted','ACT/360 unconverted'],[0.,1e4*(row['converted360_loss']/row['act365_loss']-1),1e4*(row['naive360_loss']/row['act365_loss']-1)],color=['#0072B2','#009E73','#D55E00'])
    ax[0].set_ylabel('Relative loss difference (basis points vs ACT/365F)');ax[0].set_title('Same physical forces require unit conversion');ax[0].tick_params(axis='x',rotation=15)
    ax[0].text(.02,.98,'Synthetic 30-day EAD100→20; d=.24, p=1.2, r=.06',transform=ax[0].transAxes,va='top',fontsize=8)
    ax[1].plot([a['hours_after_valuation'] for a in audits],[int(a['accepted']) for a in audits],'o')
    ax[1].axvline(0,color='black',linestyle='--');ax[1].set(xlabel='Declared source availability − valuation (hours)',ylabel='Accepted (1=yes, 0=no)',title='Temporal gate on declared metadata',yticks=[0,1])
    fig.savefig('results/dated.png',dpi=150);plt.close(fig)
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':main()
