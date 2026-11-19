"""One-month UCI default benchmark, with hypothetical loss proxies, not 12-month ECL."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
PRODUCTS = HERE.parents[1]
SOURCE = PRODUCTS / 'scorecard-logistico-woe/observed-uci350/data/default-of-credit-card-clients.xls'
HASH = '30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933'
FEATURES = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
TARGET = 'default payment next month'


def validate(frame, expected_n=None):
    columns = ['ID', 'LIMIT_BAL', *FEATURES, TARGET]
    if not set(columns).issubset(frame.columns) or (expected_n is not None and len(frame) != expected_n):
        raise ValueError('Unexpected source schema or row count')
    data = frame[columns].copy()
    data[columns] = data[columns].apply(pd.to_numeric, errors='raise')
    if data.empty or not np.isfinite(data.to_numpy()).all() or data.ID.duplicated().any():
        raise ValueError('Nonfinite values or duplicate identifiers')
    if (data.LIMIT_BAL <= 0).any() or not data[TARGET].isin([0, 1]).all():
        raise ValueError('Invalid target or limit')
    if not np.equal(data[FEATURES], np.floor(data[FEATURES])).to_numpy().all():
        raise ValueError('Payment history categories must be integers')
    return data


def evaluate(train, test, bootstrap=500, seed=42):
    """Fit only on train; bootstrap paired Brier differences conditional on fitted model."""
    if bootstrap < 1 or not isinstance(bootstrap, int):
        raise ValueError('bootstrap must be a positive integer')
    y_train, y = train[TARGET].to_numpy(), test[TARGET].to_numpy()
    if set(y_train) != {0, 1} or set(y) != {0, 1}:
        raise ValueError('Both outcome classes required in train and test')
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))
    model.fit(train[FEATURES], y_train)
    probability = model.predict_proba(test[FEATURES])[:, 1]
    base = float(y_train.mean())
    base_error = (base - y) ** 2
    model_error = (probability - y) ** 2
    improvement = base_error - model_error
    rng = np.random.default_rng(seed)
    boot = [float(improvement[rng.integers(0, len(y), len(y))].mean()) for _ in range(bootstrap)]
    # qcut duplicates='drop' avoids splitting identical model probabilities into arbitrary groups.
    table = pd.DataFrame({'pd': probability, 'outcome': y})
    table['bin'] = pd.qcut(table['pd'], q=10, duplicates='drop')
    bins = table.groupby('bin', observed=True).agg(n=('outcome', 'size'), predicted=('pd', 'mean'), observed=('outcome', 'mean')).reset_index(drop=True)
    lgd = .45
    exposure = test.LIMIT_BAL.to_numpy(dtype=float)
    return {'n_train': len(train), 'n_test': len(test), 'train_default_rate': base,
            'test_default_rate': float(y.mean()),
            'baseline': {'brier': float(brier_score_loss(y, np.repeat(base, len(y)))),
                         'log_loss': float(log_loss(y, np.repeat(base, len(y)), labels=[0, 1]))},
            'model': {'brier': float(brier_score_loss(y, probability)), 'auc': float(roc_auc_score(y, probability)),
                      'log_loss': float(log_loss(y, probability, labels=[0, 1]))},
            'brier_improvement_baseline_minus_model': float(improvement.mean()),
            'brier_improvement_bootstrap_95pct_conditional_on_fit': [float(x) for x in np.quantile(boot, [.025, .975])],
            'calibration_bins': bins.to_dict(orient='records'),
            'hypothetical_lgd': lgd, 'sum_limit_twd': float(exposure.sum()),
            'expected_proxy_loss_twd': float(np.sum(probability * lgd * exposure)),
            'default_label_weighted_proxy_loss_twd': float(np.sum(y * lgd * exposure)),
            'interpretation': 'One-month payment label in Taiwan, random holdout; credit limit is not EAD and proxy loss is not observed loss.'}


def main():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != HASH:
        raise ValueError('Source hash mismatch')
    data = validate(pd.read_excel(SOURCE, header=1), expected_n=30000)
    train, test = train_test_split(data, test_size=.25, random_state=42, stratify=data[TARGET])
    result = {'source_sha256': HASH, 'split': 'stratified random 75/25, seed 42', 'features': FEATURES,
              **evaluate(train, test)}
    print(json.dumps(result, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
