"""CAS/S&P Schedule P: reproducible age-to-age benchmark; no tail beyond age 10."""
from pathlib import Path
import hashlib
import subprocess
import numpy as np
import pandas as pd

URL = 'https://www.casact.org/sites/default/files/2026-03/ppauto_pos98-07%20%281%29.csv'
EXPECTED_SHA256 = '6e838f1e44c67218133ef1c8e28ca2b34b9f21ba4ee94de408c412638f798d96'
COMPANY = 1767  # State Farm Mut Grp; preselected demonstrative insurer


def load_data(path):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['curl', '-fsSL', '--max-time', '90', URL, '-o', str(path)], check=True)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA256:
        raise ValueError(f'CAS snapshot changed: SHA-256 {sha}; audit the new vintage before use')
    data = pd.read_csv(path)
    data = data[data.GRCODE == COMPANY].copy()
    assert len(data) == 100 and not data.duplicated(['AccidentYear', 'DevelopmentLag']).any()
    assert data.CumPaidLoss.notna().all() and (data.CumPaidLoss > 0).all()
    data['calendar_year'] = data.AccidentYear + data.DevelopmentLag - 1
    assert (data.calendar_year == data.DevelopmentYear).all()
    return data, sha


def fit_factors(data, cutoff, recent=None):
    """Volume-weighted link ratios computed only from cells visible at cutoff."""
    observed = data.loc[data.calendar_year <= cutoff]
    table = observed.pivot(index='AccidentYear', columns='DevelopmentLag', values='CumPaidLoss')
    factors = []
    for j in range(1, 10):
        pair = table.reindex(columns=[j, j + 1]).dropna().sort_index()
        if recent is not None:
            pair = pair.tail(recent)
        if pair.empty or (pair[j] <= 0).any():
            raise ValueError(f'No valid age-{j} pairs at cutoff {cutoff}')
        factors.append({'lag': j, 'n_pairs': len(pair), 'factor': pair[j+1].sum()/pair[j].sum()})
    return pd.DataFrame(factors)


def backtest(data, cutoff=2007, recent=None):
    """Forecast each age-10 ultimate vs held-out complete lower triangle."""
    factors = fit_factors(data, cutoff, recent)
    f = factors.set_index('lag').factor
    observed = data.loc[data.calendar_year <= cutoff]
    diagonal = observed.sort_values('DevelopmentLag').groupby('AccidentYear').tail(1)
    ultimate = data.loc[data.DevelopmentLag == 10, ['AccidentYear', 'CumPaidLoss']].rename(columns={'CumPaidLoss':'actual_age10'})
    rows = []
    for _, d in diagonal.iterrows():
        age = int(d.DevelopmentLag)
        if age >= 10:
            continue
        estimate = float(d.CumPaidLoss) * float(np.prod([f[j] for j in range(age,10)]))
        rows.append({'AccidentYear':int(d.AccidentYear), 'age':age, 'paid_to_cutoff':float(d.CumPaidLoss), 'predicted_age10':estimate})
    result = pd.DataFrame(rows).merge(ultimate, on='AccidentYear', how='left', validate='one_to_one')
    assert result.actual_age10.notna().all()
    result['reserve_predicted'] = result.predicted_age10-result.paid_to_cutoff
    result['future_paid_age10'] = result.actual_age10-result.paid_to_cutoff
    result['error'] = result.reserve_predicted-result.future_paid_age10
    return factors, result
