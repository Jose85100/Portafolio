"""Run the synthetic IFRS 9 model laboratory; never downloads customer data."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import numpy as np
from src.multimodel.experiment import fit_experiment
from src.multimodel.validation import bootstrap_mean_interval


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'results'/'multimodel')
    parser.add_argument('--save-monthly',action='store_true',help='Also export all baseline monthly contributions')
    parser.add_argument('--config',type=Path,default=Path(__file__).parent/'configs'/'reference.json')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    config=json.loads(args.config.read_text())
    ex=fit_experiment(config['history_accounts'],config['reporting_accounts'],config['seed']); ex['comparison'].to_csv(args.output/'ecl_comparison.csv',index=False,float_format='%.10g')
    ex['pd_metrics'].to_csv(args.output/'pd_oot_metrics.csv',index=False,float_format='%.10g')
    from src.multimodel import run_ecl
    reference=run_ecl(ex['loans'],ex['pd_models'][0],ex['lgd_models'][0],ex['ead_models'][0],ex['scenarios'])
    reference['loans'].to_csv(args.output/'baseline_loans.csv',float_format='%.10g')
    reference['scenarios'].to_csv(args.output/'baseline_scenarios.csv',index=False,float_format='%.10g')
    if args.save_monthly: reference['monthly'].to_csv(args.output/'baseline_monthly.csv',index=False,float_format='%.10g')
    keys=list(ex['by_loan']); baseline=ex['by_loan'][keys[0]]
    intervals=[]
    for key,values in ex['by_loan'].items():
        low,high=bootstrap_mean_interval(values-baseline)
        intervals.append(dict(configuration=key,mean_delta=float(np.mean(values-baseline)),low=low,high=high))
    import pandas as pd
    pd.DataFrame(intervals).to_csv(args.output/'paired_ecl_bootstrap.csv',index=False,float_format='%.10g')
    root=Path(__file__).parent
    diagnostics=[]
    w=ex['workouts'].query('completion_month >= 30')
    for model in ex['lgd_models'][:2]:
        predicted=model.predict(w,[0.],np.ones((len(w),1)))[:,0] if model.model_id=='lgd_segment_workout' else model.regression.predict(w[['collateral_ratio','segment','macro']])
        diagnostics.append(dict(component='LGD',model=model.model_id,n=len(w),mae=float(np.mean(np.abs(predicted-w.loss_fraction))),rmse=float(np.mean((predicted-w.loss_fraction)**2)**.5),bias=float(np.mean(predicted-w.loss_fraction))))
    c=ex['windows'].query('completion_month >= 30');fitted=ex['ead_models'][1].ccf_model
    for name,predicted in [('fixed_ccf',np.full(len(c),.5)),('fractional_ccf',fitted.predict(c.utilization,c.segment,c.macro))]:
        diagnostics.append(dict(component='CCF',model=name,n=len(c),mae=float(np.mean(np.abs(predicted-c.ccf))),rmse=float(np.mean((predicted-c.ccf)**2)**.5),bias=float(np.mean(predicted-c.ccf))))
    pd.DataFrame(diagnostics).to_csv(args.output/'component_holdout_metrics.csv',index=False,float_format='%.10g')
    fitted_parameters={}
    for m in ex['pd_models'][:2]:
        fitted_parameters[m.model_id]=dict(intercept=m.estimator.intercept_.tolist(),coefficients=m.estimator.coef_.tolist())
    fitted_parameters['pd_rating_transitions']=dict(matrix=ex['pd_models'][2].matrix.tolist(),macro_beta=ex['pd_models'][2].macro_beta)
    fitted_parameters['lgd_segment_workout']={str(k):v for k,v in ex['lgd_models'][0].means.items()}
    for name,m in [('lgd_fractional_workout',ex['lgd_models'][1].regression),('ccf_fractional',fitted.regression)]:
        fitted_parameters[name]=dict(location=m.location.tolist(),scale=m.scale.tolist(),coefficients=m.coefficients.tolist())
    (args.output/'fitted_parameters.json').write_text(json.dumps(fitted_parameters,indent=2)+'\n')
    manifest=dict(seed=config['seed'],history_accounts=config['history_accounts'],reporting_accounts=config['reporting_accounts'],
        reporting_seed=61,train_accounts=len(ex['train_ids']),oot_accounts=len(ex['oot']), configurations=len(ex['comparison']),
        provenance='Fully synthetic; no Colombian portfolio calibration or external validation',
        units='arbitrary monetary units, annual effective rates, monthly default buckets',
        split='Train origination 0..29, 36m performance ends by 65; OOT origination 66..83, retrospectively mature labels',
        stage_counts={str(k):int(v) for k,v in ex['loans'].stage.value_counts().items()},
        bootstrap='95% percentile paired account resampling; model fits/scenarios held fixed, no parameter uncertainty',
        versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn']},
        source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'src'/'multimodel').glob('*.py'))})
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(ex['pd_metrics'].to_string(index=False));print(ex['comparison'][['pd','lgd','ead','ecl']].to_string(index=False))

if __name__=='__main__': main()
