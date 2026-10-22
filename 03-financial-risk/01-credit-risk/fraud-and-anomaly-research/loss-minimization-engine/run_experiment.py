"""Synthetic reproducible benchmark. Run: python run_experiment.py."""
from pathlib import Path
import csv,json,importlib.metadata
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score,brier_score_loss,log_loss
from threadpoolctl import threadpool_limits
from src.engine import Case,Action,Scenario,optimize,expected_cost
from src.models import Models,generate,FEATURES
OUT=Path(__file__).resolve().parent/'results'
ACTIONS=[Action('allow',0,0,0,0),Action('verify',.35,4000,2500,3),Action('review',.8,18000,15000,15)]
SCENARIOS=[Scenario('base'),Scenario('lower_effectiveness',1.3,1.25,.65),Scenario('lower_prevalence',.7,1,.9)]
CAPACITY=75.


def export_csv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def fixed_review(score):
    decisions=['allow']*len(score)
    for i in np.argsort(-score,kind='stable')[:int(CAPACITY/15)]:decisions[int(i)]='review'
    return decisions


def run():
    OUT.mkdir(exist_ok=True);data=generate();models=Models().fit(data)
    idx=np.flatnonzero(models.test);scores=models.predict(data['x'][idx]);y=data['y'][idx]
    metrics=[]
    for name,p in scores.items():
        row=dict(model=name,average_precision=float(average_precision_score(y,p)),brier=None,log_loss=None,mean_prediction=None)
        if name!='novelty_score':row.update(brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,p)),mean_prediction=float(p.mean()))
        metrics.append(row)
    export_csv('model_metrics.csv',metrics)
    reliability=[]
    for name in ('logit','boosting_raw','boosting_calibrated'):
        p=scores[name]
        for k in range(10):
            mask=(p>=k/10)&((p<(k+1)/10) if k<9 else (p<=1))
            if mask.any():reliability.append(dict(model=name,bin_lower=k/10,count=int(mask.sum()),mean_probability=float(p[mask].mean()),observed_rate=float(y[mask].mean())))
    export_csv('reliability.csv',reliability)
    daily=[];exports=[];lookup={a.name:a for a in ACTIONS}
    for day in np.unique(data['time'][idx]):
        loc=np.flatnonzero(data['time'][idx]==day);global_idx=idx[loc];p=scores['boosting_calibrated'][loc]
        cases=[Case(str(i),float(prob),float(data['loss'][i])) for i,prob in zip(global_idx,p)]
        expected=optimize(cases,ACTIONS,CAPACITY,SCENARIOS,[.6,.25,.15])
        robust=optimize(cases,ACTIONS,CAPACITY,SCENARIOS,objective='worst_case')
        review_only=optimize(cases,[ACTIONS[0],ACTIONS[2]],CAPACITY,SCENARIOS,[.6,.25,.15])
        logit_cases=[Case(str(i),float(prob),float(data['loss'][i])) for i,prob in zip(global_idx,scores['logit'][loc])]
        logit_plan=optimize(logit_cases,ACTIONS,CAPACITY,SCENARIOS,[.6,.25,.15])
        rules=np.nansum(data['x'][global_idx]>.6,axis=1)
        plans=dict(allow_all=['allow']*len(loc),rules_rank=fixed_review(rules),probability_rank=fixed_review(p),economic_review_only=review_only['actions'],economic_logit=logit_plan['actions'],expected_loss=expected['actions'],scenario_minimax=robust['actions'])
        for name,decisions in plans.items():
            effort=sum(lookup[a].effort_minutes for a in decisions)
            if effort>CAPACITY+1e-6:raise AssertionError('capacity')
            predicted=oracle=conditional=friction=0.
            for j,a_name in enumerate(decisions):
                i=global_idx[j];action=lookup[a_name]
                evaluation_p=float(scores['logit'][loc[j]]) if name=='economic_logit' else float(p[j])
                predicted+=expected_cost(Case(str(i),evaluation_p,float(data['loss'][i])),action)
                oracle+=expected_cost(Case(str(i),float(data['p_true'][i]),float(data['loss'][i])),action)
                conditional+=(data['y'][i]*data['loss'][i]*(1-action.prevent_fraction)+action.cost_cop+(1-data['y'][i])*action.legitimate_friction_cop)
                friction+=(1-data['y'][i])*action.legitimate_friction_cop
                exports.append(dict(day=int(day),case_id=str(i),policy=name,action=a_name,predicted_probability=evaluation_p,loss_cop=float(data['loss'][i])))
            daily.append(dict(day=int(day),policy=name,minutes=effort,reviews=decisions.count('review'),verifications=decisions.count('verify'),predicted_base_cost_cop=float(predicted),simulator_expected_cost_cop=float(oracle),label_conditional_assumed_cost_cop=float(conditional),legitimate_friction_cop=float(friction)))
    export_csv('policy_daily.csv',daily);export_csv('decisions.csv',exports)
    baseline=sum(r['simulator_expected_cost_cop'] for r in daily if r['policy']=='allow_all');summary=[]
    for name in plans:
        subset=[r for r in daily if r['policy']==name];total=sum(r['simulator_expected_cost_cop'] for r in subset)
        summary.append(dict(policy=name,simulator_expected_cost_cop=total,savings_vs_allow_all_cop=baseline-total,minutes=sum(r['minutes'] for r in subset),label_conditional_assumed_cost_cop=sum(r['label_conditional_assumed_cost_cop'] for r in subset)))
    export_csv('policy_summary.csv',summary)
    base=np.array([r['simulator_expected_cost_cop'] for r in daily if r['policy']=='probability_rank'])
    chosen=np.array([r['simulator_expected_cost_cop'] for r in daily if r['policy']=='expected_loss'])
    delta=base-chosen;rng=np.random.default_rng(33)
    boot=delta[rng.integers(0,len(delta),(2000,len(delta)))].sum(axis=1)
    sensitivity=[]
    for factor in (0.,.4,.7,1.,1.2):
        scenario=Scenario('efficacy_stress',1,1,factor)
        for name in ('probability_rank','expected_loss','scenario_minimax'):
            total=0.
            for row in exports:
                if row['policy']!=name:continue
                i=int(row['case_id']);total+=expected_cost(Case(str(i),float(data['p_true'][i]),float(data['loss'][i])),lookup[row['action']],scenario)
            sensitivity.append(dict(effectiveness_multiplier=factor,policy=name,simulator_expected_cost_cop=total))
    export_csv('effectiveness_sensitivity.csv',sensitivity)
    metadata=dict(seed=20261021,test_days=len(delta),test_n=len(idx),test_positives=int(y.sum()),test_prevalence=float(y.mean()),train_n=int(models.train.sum()),calibration_n=int(models.calibration.sum()),training_label_cutoff=80,calibration_label_cutoff=110,test_start=110,capacity_minutes_per_day=CAPACITY,policy_model='boosting_calibrated (prespecified)',cost_interpretation='simulation under assumed efficacy, not observed avoided loss',paired_savings_vs_probability_rank_cop=float(delta.sum()),paired_day_bootstrap_95_cop=np.quantile(boot,[.025,.975]).tolist(),logit_coefficients=models.logit.coef_.tolist(),training_medians=models.medians.tolist(),feature_names=list(FEATURES)+[f'{f}_missing' for f in FEATURES],calibrator_coefficient=models.calibrator.coef_.tolist(),calibrator_intercept=models.calibrator.intercept_.tolist(),versions={n:importlib.metadata.version(n) for n in ('numpy','scipy','scikit-learn','matplotlib','threadpoolctl')})
    (OUT/'experiment.json').write_text(json.dumps(metadata,indent=2,allow_nan=False)+'\n')
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'font.size':10,'figure.dpi':150})
    fig,ax=plt.subplots(figsize=(8,5.3));ax.barh([r['policy'] for r in summary],[r['simulator_expected_cost_cop']/1e6 for r in summary],color=['#8996A8','#6295BF','#438D9B','#60A7A0','#55825A','#24756C','#615194'])
    ax.invert_yaxis();ax.set_xlabel('Costo esperado simulado (millones COP)');ax.set_title('Presupuesto diario: 75 minutos\nEficacia supuesta y datos sintéticos');fig.tight_layout();fig.savefig(OUT/'policy_cost.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5))
    for name,color in zip(('probability_rank','expected_loss','scenario_minimax'),('#6295BF','#24756C','#615194')):
        subset=[r for r in sensitivity if r['policy']==name];ax.plot([r['effectiveness_multiplier'] for r in subset],[r['simulator_expected_cost_cop']/1e6 for r in subset],marker='o',label=name,color=color)
    ax.axhline(baseline/1e6,color='#9A593C',linestyle='--',label='allow_all');ax.set_xlabel('Multiplicador de eficacia supuesto');ax.set_ylabel('Costo esperado simulado (millones COP)');ax.set_title('Políticas congeladas: sensibilidad a eficacia\nNo representa pérdidas evitadas observadas');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'efficacy_stress.png');plt.close(fig)
    print(json.dumps(dict(metrics=metrics,policies=summary,bootstrap=metadata['paired_day_bootstrap_95_cop']),indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=1):run()
