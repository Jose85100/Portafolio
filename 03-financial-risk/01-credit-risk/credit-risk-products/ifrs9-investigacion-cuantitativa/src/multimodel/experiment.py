"""Deterministic model fitting and 3 x 3 x 2 factorial ECL comparison."""
from itertools import product
import numpy as np
import pandas as pd
from . import (LogisticPD, SurvivalPD, TransitionPD, SegmentLGD, RegressionLGD,
               CashflowLGD, CCFModel, ExposureModel, classify, run_ecl)
from .data import synthetic_history, reporting_portfolio, standard_scenarios
from .validation import binary_metrics


def fit_experiment(n_history=2200, n_reporting=180, seed=20261018):
    cohort, panel, transitions, workouts, windows = synthetic_history(n_history, seed)
    # First 30 origination months are training. All labels are retrospectively
    # mature; OOT starts at month 66, after the 36m training performance window.
    # Originations 30..65 are embargoed; generated OOT origination dates shift +36.
    train_ids = set(cohort.loc[cohort.origination_month < 30, 'loan_id'])
    train = cohort.loan_id.isin(train_ids)
    cohort.loc[~train, 'origination_month'] += 36
    panel.loc[~panel.loan_id.isin(train_ids), 'origination_month'] += 36
    transitions.loc[~transitions.loan_id.isin(train_ids), 'origination_month'] += 36
    pd_models = [LogisticPD().fit(cohort.loc[train]),
                 SurvivalPD().fit(panel.loc[panel.loan_id.isin(train_ids)]),
                 TransitionPD().fit(transitions.loc[transitions.loan_id.isin(train_ids)])]
    wtrain = workouts.completion_month < 30
    ctrain = windows.completion_month < 30
    lgd_models = [SegmentLGD().fit(workouts.loc[wtrain]), RegressionLGD().fit(workouts.loc[wtrain]), CashflowLGD()]
    ccf = CCFModel().fit(windows.loc[ctrain])
    ead_models = [ExposureModel(), ExposureModel(annual_cpr=.12, ccf_model=ccf)]
    loans = reporting_portfolio(n_reporting)
    loans = loans.join(classify(loans)); scenarios = standard_scenarios()
    # Cohort risk characteristics at origination for PD diagnostics; use each
    # account's known baseline macro across all 12 months for comparable labels.
    oot = cohort.loc[~train].copy(); oot['age_months']=0
    oot['rating'] = np.digitize(-oot.score,[-.4,.6])
    metrics = []; predictions = {}
    for model in pd_models:
        prediction = np.array([model.predict_curve(oot.iloc[[i]], np.repeat(row.macro,12)).sum()
                               for i,row in enumerate(oot.itertuples())])
        predictions[model.model_id] = prediction
        metrics.append({'model':model.model_id, **binary_metrics(oot.default_12m,prediction)})
    results = []; baseline = None; by_loan = {}
    for p,l,e in product(pd_models,lgd_models,ead_models):
        run = run_ecl(loans,p,l,e,scenarios); key='|'.join(run['models'].values())
        total = float(run['loans'].ecl.sum()); by_loan[key]=run['loans'].ecl.to_numpy()
        if baseline is None: baseline=total
        results.append({'configuration':key, **run['models'], 'ecl':total,
                        'coverage':total/loans.balance.sum(), 'delta_baseline':total-baseline,
                        **{f'stage_{s}':float(run['loans'].loc[run['loans'].stage==s,'ecl'].sum()) for s in [1,2,3]}})
    return dict(cohort=cohort,panel=panel,transitions=transitions,workouts=workouts,windows=windows,
                pd_models=pd_models,lgd_models=lgd_models,ead_models=ead_models,loans=loans,
                scenarios=scenarios,oot=oot,predictions=predictions,pd_metrics=pd.DataFrame(metrics),
                comparison=pd.DataFrame(results),by_loan=by_loan,train_ids=train_ids)
