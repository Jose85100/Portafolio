"""Fully synthetic reproducible fixtures; no customer data or Colombian calibration."""
import numpy as np
import pandas as pd
from scipy.special import expit
from .contracts import integer
from .engine import Scenario


def synthetic_history(n=2200, seed=20261018):
    integer(n, 'n', 100000); rng = np.random.default_rng(seed)
    cohort = pd.DataFrame({'loan_id':np.arange(n), 'score':rng.normal(size=n),
        'segment':rng.integers(0, 2, n), 'macro':rng.normal(0, .6, n),
        'origination_month':rng.integers(0, 48, n)})
    rows = []; outcomes = []; transition_rows = []
    base = np.array([[.94,.045,.012,.003],[.025,.92,.045,.01],[.005,.04,.925,.03],[0,0,0,1.]])
    for row in cohort.itertuples():
        default12 = 0
        for m in range(1, 37):
            hazard = expit(-5.2-.65*row.score+.4*row.segment+.4*row.macro+.22*np.log1p(m)/4)
            event = int(rng.random() < hazard)
            rows.append((row.loan_id, m, m-1, row.score, row.segment, row.macro, event, row.origination_month))
            if event:
                default12 = int(m <= 12); break
        outcomes.append(default12)
        # Independent synthetic rating process: comparator is misspecified versus
        # the continuous hazard generator; this is deliberate and documented.
        rating = int(np.digitize(-row.score, [-.4, .6]))
        for m in range(1, 37):
            nxt = int(rng.choice(4, p=base[rating]))
            transition_rows.append((row.loan_id, m, rating, nxt, row.origination_month))
            rating = nxt
            if rating == 3: break
    cohort['default_12m'] = outcomes
    panel = pd.DataFrame(rows, columns=['loan_id','month','age_months','score','segment','macro','default','origination_month'])
    transitions = pd.DataFrame(transition_rows, columns=['loan_id','month','from_state','to_state','origination_month'])
    # Independent closed workout observations. Future/censored recoveries are not
    # silently treated as zero. Gross/cost timing is compressed into this target.
    count = max(n//2, 300)
    workouts = pd.DataFrame({'collateral_ratio':rng.uniform(0, 1.8, count),
        'segment':rng.integers(0,2,count), 'macro':rng.normal(0,.7,count),
        'completion_month':rng.integers(0,48,count)})
    mean = expit(.2-1.4*workouts.collateral_ratio+.3*workouts.segment+.35*workouts.macro)
    workouts['loss_fraction'] = rng.beta(mean*18, (1-mean)*18)
    windows = pd.DataFrame({'utilization':rng.uniform(.1,.95,count), 'segment':rng.integers(0,2,count),
        'macro':rng.normal(0,.7,count), 'completion_month':rng.integers(0,48,count)})
    ccf = expit(-.7+.9*windows.utilization+.2*windows.segment+.3*windows.macro)
    windows['ccf'] = rng.beta(ccf*25, (1-ccf)*25)
    return cohort, panel, transitions, workouts, windows


def reporting_portfolio(n=180, seed=61, horizon=36):
    integer(n, 'n', 100000); integer(horizon, 'horizon'); rng = np.random.default_rng(seed)
    score = rng.normal(size=n); balance = rng.lognormal(9, .6, n)
    loans = pd.DataFrame({'loan_id':np.arange(100000,100000+n), 'score':score,
        'segment':rng.integers(0,2,n), 'age_months':rng.integers(0,25,n),
        'rating':np.digitize(-score,[-.4,.6]), 'balance':balance,
        'limit':balance*rng.uniform(1,2,n), 'coupon':rng.uniform(.08,.30,n),
        'eir':rng.uniform(.08,.25,n), 'term_months':rng.integers(min(6,horizon),horizon+1,n),
        'product':rng.choice(['term','revolver'],n,p=[.7,.3]),
        'collateral_ratio':rng.uniform(0,1.8,n), 'dpd':rng.choice([0,15,35,95],n,p=[.78,.10,.09,.03]),
        'credit_impaired':False, 'watchlist':rng.random(n)<.04})
    loans['origin_lifetime_pd'] = expit(-2.5-.6*score)
    loans['current_lifetime_pd'] = np.clip(loans.origin_lifetime_pd*rng.uniform(.8,3,n),0,1)
    loans['recovery_times'] = [(1.,2.,3.)]*n
    loans['recovery_cashflows'] = [tuple(b*np.array([.3,.12,.06])) for b in balance]
    return loans


def standard_scenarios(horizon=36):
    integer(horizon, 'horizon')
    # Standardized macro risk factor, NOT GDP, unemployment or a confidence band.
    t = np.arange(horizon)
    return [Scenario('base',.6,tuple(np.zeros(horizon))),
            Scenario('adverse',.3,tuple(1.5*np.exp(-t/24)),.85,.5),
            Scenario('upside',.1,tuple(-.8*np.exp(-t/24)),1.08,0.)]
