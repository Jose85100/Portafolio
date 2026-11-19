"""UCI card limit as a stress exposure proxy; no observed credit losses."""
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile

import pandas as pd

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1]
RISK_ROOT = ENGINE.parent
SOURCE = RISK_ROOT / '01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/data/default-of-credit-card-clients.xls'
EXPECTED = '30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933'


def prepare(frame):
    required = ['ID', 'LIMIT_BAL', 'default payment next month']
    if any(c not in frame for c in required) or len(frame) != 30000:
        raise ValueError('Unexpected UCI schema or row count')
    data = frame[required].copy()
    data[required] = data[required].apply(pd.to_numeric, errors='raise')
    if data.isna().any().any() or data.ID.duplicated().any():
        raise ValueError('Missing values or duplicate IDs')
    if not data['default payment next month'].isin([0, 1]).all() or not (data.LIMIT_BAL > 0).all():
        raise ValueError('Invalid limit or target')
    order = list(range(len(data)))
    random.Random(42).shuffle(order)
    n_train = 22500
    return data.iloc[order[:n_train]], data.iloc[order[n_train:]]


def segment_pd(train, test):
    """Fit two training-only quantiles and within-bin observed default rates."""
    cuts = [float(train.LIMIT_BAL.quantile(1/3)), float(train.LIMIT_BAL.quantile(2/3))]
    if not cuts[0] < cuts[1]:
        raise ValueError('Training quantile cut points are not distinct')
    def bins(frame):
        return (frame.LIMIT_BAL > cuts[0]).astype(int) + (frame.LIMIT_BAL > cuts[1]).astype(int)
    train_bins = bins(train)
    rates = train.groupby(train_bins)['default payment next month'].mean()
    if set(rates.index) != {0, 1, 2}:
        raise ValueError('Empty training segment')
    return cuts, [float(rates[i]) for i in range(3)], bins(test).map(rates)


def main():
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if source_hash != EXPECTED:
        raise ValueError('UCI source hash mismatch')
    frame = pd.read_excel(SOURCE, header=1)
    train, test = prepare(frame)
    pd_estimate = float(train['default payment next month'].mean())
    lgd = 0.45  # illustrative, no recoveries in UCI
    cuts, rates, segmented = segment_pd(train, test)
    def rows(pds):
        return ''.join(f'{pd:.17g} {lgd} {limit:.17g}\n' for pd, limit in zip(pds, test.LIMIT_BAL))
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / 'risk_engine'
        subprocess.run(['c++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(ENGINE / 'cpp/include'), str(HERE / 'engine_cli.cpp'), '-o', str(exe)], check=True)
        output = subprocess.run([str(exe)], input=rows([pd_estimate] * len(test)), text=True, capture_output=True, check=True).stdout
        segmented_output = subprocess.run([str(exe)], input=rows(segmented), text=True, capture_output=True, check=True).stdout
    el, variance = map(float, output.split())
    segment_el, segment_variance = map(float, segmented_output.split())
    proxy_realized = float((test.LIMIT_BAL * test['default payment next month'] * lgd).sum())
    result = {'source_sha256': source_hash, 'seed': 42, 'n_train': len(train), 'n_test': len(test),
              'training_default_rate': pd_estimate, 'test_default_rate': float(test['default payment next month'].mean()),
              'training_limit_cutpoints_twd': cuts, 'training_segment_default_rates': rates,
              'test_brier_global': float(((test['default payment next month'] - pd_estimate) ** 2).mean()),
              'test_brier_segmented': float(((test['default payment next month'] - segmented) ** 2).mean()),
              'segmented_expected_proxy_loss_twd': segment_el, 'segmented_independent_variance_twd2': segment_variance,
              'lgd_assumption': lgd, 'test_limit_sum_twd': float(test.LIMIT_BAL.sum()),
              'expected_proxy_loss_twd': el, 'realized_proxy_loss_twd': proxy_realized,
              'independent_default_proxy_variance_twd2': variance,
              'interpretation': 'Credit limit, not EAD; fixed LGD hypothetical; proxy loss is not observed loss. Random split within 2005, not out-of-time.'}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
