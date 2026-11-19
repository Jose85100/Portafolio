"""Chronological, capacity-constrained ULB transaction-fraud benchmark.

External benchmark: use only with the documented original CSV. No data download
or write occurs here; stdout is a small JSON of aggregate statistics.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

EXPECTED_MD5 = 'e90efcb83d69faf99fcab8b0255024de'
FEATURES = [f'V{i}' for i in range(1, 29)] + ['Amount']


def validate(frame, full=True):
    columns = ['Time', *FEATURES, 'Class']
    if list(frame.columns) != columns:
        raise ValueError('Unexpected schema or feature order')
    if full and len(frame) != 284807:
        raise ValueError('Unexpected row count')
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError('Missing or non-finite value')
    if not frame.Class.isin([0, 1]).all() or (frame.Time < 0).any() or (frame.Amount < 0).any():
        raise ValueError('Invalid label, time or amount')
    if full and int(frame.Class.sum()) != 492:
        raise ValueError('Unexpected fraud count')


def temporal_split(frame):
    """60/20/20 by row quantiles; timestamps tied at boundaries stay together."""
    n = len(frame)
    if n < 10:
        raise ValueError('At least 10 rows required')
    ordered = np.sort(frame.Time.to_numpy())
    a, b = ordered[int(n * .6)], ordered[int(n * .8)]
    if a >= b:
        raise ValueError('Not enough distinct time values')
    train = frame[frame.Time < a]
    valid = frame[(frame.Time >= a) & (frame.Time < b)]
    test = frame[frame.Time >= b]
    if any(len(x) == 0 or x.Class.nunique() != 2 for x in (train, valid, test)):
        raise ValueError('Empty partition or only one class')
    return train, valid, test


def topk_metrics(y, scores, fraction):
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if len(y) == 0 or len(y) != len(scores) or not 0 < fraction <= 1 or not np.isfinite(scores).all() or not np.isin(y, [0, 1]).all():
        raise ValueError('Invalid labels, scores or capacity')
    # Stable ties use original input order. Results describe retrospective ranking
    # within each complete block, not a real-time capacity scheduler.
    k = math.ceil(len(y) * fraction)
    idx = np.argsort(-scores, kind='stable')[:k]
    tp = int(y[idx].sum())
    return {'capacity_fraction': fraction, 'alerts': k, 'true_positives': tp,
            'precision': tp/k, 'recall': tp/int(y.sum()) if y.sum() else None}


def run(frame, file_hash):
    validate(frame)
    train, valid, test = temporal_split(frame)
    def x(part):
        z = part[FEATURES].copy()
        z['Amount'] = np.log1p(z['Amount'])
        return z
    model = make_pipeline(StandardScaler(), LogisticRegression(solver='liblinear', max_iter=500, random_state=42))
    model.fit(x(train), train.Class)
    blocks = {}
    for name, part in [('train', train), ('validation', valid), ('test', test)]:
        info = {'rows': len(part), 'frauds': int(part.Class.sum()), 'prevalence': float(part.Class.mean()),
                'time_min_seconds': float(part.Time.min()), 'time_max_seconds': float(part.Time.max())}
        if name != 'train':
            logits = model.predict_proba(x(part))[:, 1]
            info['logistic'] = {'average_precision': float(average_precision_score(part.Class, logits)),
                                'at_1pct': topk_metrics(part.Class, logits, .01)}
            info['amount_rule'] = {'average_precision': float(average_precision_score(part.Class, part.Amount)),
                                   'at_1pct': topk_metrics(part.Class, part.Amount, .01)}
        blocks[name] = info
    return {'source_md5': file_hash, 'evaluation': 'time block rankings; 1% capacity; ties by input order',
            'partitions': blocks}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, type=Path, help='Local source creditcard.csv (not stored in repository)')
    args = ap.parse_args()
    digest = hashlib.md5(args.input.read_bytes()).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError('Source MD5 does not match Zenodo record')
    frame = pd.read_csv(args.input)
    print(json.dumps(run(frame, digest), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
