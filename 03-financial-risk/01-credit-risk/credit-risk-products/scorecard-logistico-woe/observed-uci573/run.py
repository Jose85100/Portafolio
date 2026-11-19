"""UCI 573 historical classification benchmark; not population PD or ECL."""
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'data/south-german-credit-update.zip'
SHA256 = '0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551'
CATEGORICAL = ['laufkont', 'moral', 'sparkont', 'beszeit', 'rate']
NUMERIC = ['laufzeit']
FEATURES = CATEGORICAL + NUMERIC
TARGET = 'kredit'


def validate(df, expected_n=None):
    if df.empty or not set(FEATURES + [TARGET]).issubset(df.columns):
        raise ValueError('missing columns or empty input')
    if expected_n is not None and len(df) != expected_n:
        raise ValueError('invalid row count')
    df = df.copy()
    for name in FEATURES + [TARGET]:
        df[name] = pd.to_numeric(df[name], errors='raise')
    if not np.isfinite(df[FEATURES + [TARGET]].to_numpy(dtype=float)).all():
        raise ValueError('nonfinite values')
    if not df[TARGET].isin([0, 1]).all() or (df.laufzeit <= 0).any():
        raise ValueError('invalid target or duration')
    domains = {'laufkont': (1, 4), 'moral': (0, 4), 'sparkont': (1, 5),
               'beszeit': (1, 5), 'rate': (1, 4)}
    for col, (lo, hi) in domains.items():
        if not (df[col].between(lo, hi) & (df[col] == np.floor(df[col]))).all():
            raise ValueError('invalid category: ' + col)
    return df


def load_data(path=SOURCE):
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('UCI zip hash mismatch')
    with zipfile.ZipFile(path) as archive:
        with archive.open('SouthGermanCredit.asc') as f:
            frame = pd.read_csv(f, sep=r'\s+')
    frame = validate(frame, 1000)
    if int((frame[TARGET] == 0).sum()) != 300:
        raise ValueError('Unexpected label counts')
    return frame


def evaluate(train, test, seed=42, bootstrap=1000):
    if isinstance(bootstrap, bool) or not isinstance(bootstrap, int) or bootstrap < 2:
        raise ValueError('bootstrap must be integer >= 2')
    train, test = validate(train), validate(test)
    y_train, y = (1 - train[TARGET]).to_numpy(), (1 - test[TARGET]).to_numpy()
    if set(y_train) != {0, 1} or set(y) != {0, 1}:
        raise ValueError('both classes required')
    transformer = ColumnTransformer([('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL),
                                     ('num', StandardScaler(), NUMERIC)])
    model = make_pipeline(transformer, LogisticRegression(max_iter=1000, random_state=seed))
    model.fit(train[FEATURES], y_train)
    predicted = model.predict_proba(test[FEATURES])[:, 1]
    baseline = float(y_train.mean())
    delta = (baseline-y)**2 - (predicted-y)**2
    rng = np.random.default_rng(seed)
    replicates = np.array([delta[rng.integers(0, len(y), len(y))].mean() for _ in range(bootstrap)])
    calibration = pd.DataFrame({'p': predicted, 'y': y})
    calibration['bin'] = pd.qcut(calibration.p, q=5, duplicates='drop')
    groups = calibration.groupby('bin', observed=True).agg(n=('y', 'size'),
                                                           mean_predicted=('p', 'mean'),
                                                           observed_rate=('y', 'mean')).reset_index(drop=True)
    return {'train_n': len(train), 'test_n': len(test), 'train_bad_rate': baseline,
            'test_bad_rate': float(y.mean()), 'baseline_brier': float(brier_score_loss(y, np.full(len(y), baseline))),
            'model_brier': float(brier_score_loss(y, predicted)), 'model_auc': float(roc_auc_score(y, predicted)),
            'baseline_logloss': float(log_loss(y, np.full(len(y), baseline), labels=[0, 1])),
            'model_logloss': float(log_loss(y, predicted, labels=[0, 1])),
            'brier_gain_baseline_minus_model': float(delta.mean()),
            'brier_gain_bootstrap_95_conditional': [float(x) for x in np.quantile(replicates, [0.025, 0.975])],
            'calibration_groups': groups.to_dict(orient='records'),
            'overlapping_feature_patterns': len(set(map(tuple, train[FEATURES].to_numpy())) & set(map(tuple, test[FEATURES].to_numpy())))}


def main():
    data = load_data()
    train, test = train_test_split(data, test_size=.25, random_state=42, stratify=data[TARGET])
    result = {'source_sha256': SHA256, 'seed': 42, 'split': 'stratified random 75/25',
              'features': FEATURES, 'metrics': evaluate(train, test),
              'scope': 'Case-control-like historical sample with bad-credit oversampling; classification score, not a population PD.'}
    print(json.dumps(result, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
