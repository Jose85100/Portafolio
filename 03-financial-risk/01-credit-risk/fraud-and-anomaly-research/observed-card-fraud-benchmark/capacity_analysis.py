"""Capacity/frontier and frozen-threshold sensitivity on public ULB card data.

Input CSV is not included in this repository; no individual records are saved.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from run import EXPECTED_MD5, FEATURES, temporal_split, topk_metrics, validate

CAPACITIES = (0.001, 0.0025, 0.005, 0.01, 0.02)


def choose_threshold(scores, fraction):
    """Lowest score among the top ceil(n * fraction) in validation only.

    Greater-than-or-equal deployment retains all ties and may exceed budget.
    """
    s = np.asarray(scores, dtype=float)
    if s.ndim != 1 or not s.size or not np.isfinite(s).all() or not 0 < fraction <= 1:
        raise ValueError('Invalid validation scores or capacity')
    k = math.ceil(s.size * fraction)
    return float(np.sort(s)[-k])


def fixed_threshold_metrics(y, scores, threshold):
    y = np.asarray(y)
    scores = np.asarray(scores, dtype=float)
    if (y.ndim != 1 or scores.ndim != 1 or not len(y) or len(y) != len(scores)
            or not np.isin(y, [0, 1]).all() or not np.isfinite(scores).all()
            or not np.isfinite(threshold)):
        raise ValueError('Invalid outcomes, scores or threshold')
    mask = scores >= threshold
    alerts, tp, positives = int(mask.sum()), int(y[mask].sum()), int(y.sum())
    return {'threshold': float(threshold), 'alerts': alerts, 'alert_fraction': alerts / len(y),
            'true_positives': tp, 'precision': tp / alerts if alerts else None,
            'recall': tp / positives if positives else None,
            'false_positives': alerts - tp, 'false_negatives': positives - tp}


def evaluate(y_val, s_val, y_test, s_test):
    """Use validation scores to fix a threshold; test labels never set the rule."""
    if len(y_val) != len(s_val):
        raise ValueError('Invalid validation labels or scores')
    threshold = choose_threshold(s_val, .01)
    return {'frontier_test_block_ranking': [topk_metrics(y_test, s_test, c) for c in CAPACITIES],
            'validation_threshold_1pct': threshold,
            'validation_fixed_threshold': fixed_threshold_metrics(y_val, s_val, threshold),
            'test_fixed_threshold': fixed_threshold_metrics(y_test, s_test, threshold)}


def analyze(frame):
    validate(frame)
    train, valid, test = temporal_split(frame)
    def features(part):
        x = part[FEATURES].copy()
        x['Amount'] = np.log1p(x['Amount'])
        return x
    model = make_pipeline(StandardScaler(), LogisticRegression(solver='liblinear', max_iter=500, random_state=42))
    model.fit(features(train), train.Class)
    pv = model.predict_proba(features(valid))[:, 1]
    pt = model.predict_proba(features(test))[:, 1]
    return {
        'source_md5': EXPECTED_MD5,
        'train_n': len(train), 'validation_n': len(valid), 'test_n': len(test),
        'test_frauds': int(test.Class.sum()),
        'logistic': evaluate(valid.Class, pv, test.Class, pt),
        'amount_rule': evaluate(valid.Class, valid.Amount, test.Class, test.Amount),
        'note': 'Frozen threshold uses validation only; test top-k ranks the entire block retrospectively.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    digest = hashlib.md5(args.input.read_bytes()).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError('Source MD5 does not match Zenodo record')
    print(json.dumps(analyze(pd.read_csv(args.input)), indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
