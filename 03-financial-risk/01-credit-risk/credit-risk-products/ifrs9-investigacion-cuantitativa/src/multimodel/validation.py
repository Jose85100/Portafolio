"""Out-of-time diagnostics; no model selection on held-out data."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss
from .contracts import probabilities


def binary_metrics(y, p):
    y = probabilities(y, 'outcome'); p = probabilities(p, 'prediction')
    if y.shape != p.shape or not np.isin(y,[0,1]).all():
        raise ValueError('Aligned binary outcomes required')
    return {'accounts':len(y), 'defaults':int(y.sum()), 'observed_rate':float(y.mean()),
            'predicted_rate':float(p.mean()), 'brier':float(np.mean((p-y)**2)),
            'log_loss':float(log_loss(y,p,labels=[0,1])),
            'auc':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None}


def calibration(y, p, groups=8):
    probabilities(y, 'outcome'); probabilities(p, 'prediction')
    if len(y) != len(p) or len(y) < groups:
        raise ValueError('Enough aligned observations required')
    f = pd.DataFrame({'actual':np.asarray(y), 'predicted':np.asarray(p)})
    # Fixed probability edges avoid arbitrary rank splitting of identical PDs.
    f['bin'] = pd.cut(f.predicted, np.linspace(0,1,groups+1), include_lowest=True)
    return f.groupby('bin',observed=True).agg(n=('actual','size'), observed=('actual','mean'), predicted=('predicted','mean'))


def bootstrap_mean_interval(values, seed=7, repetitions=500):
    from .contracts import array, integer
    x = array(values, 'values'); integer(repetitions, 'repetitions', 10000)
    rng = np.random.default_rng(seed)
    means = [rng.choice(x, len(x), replace=True).mean() for _ in range(repetitions)]
    return tuple(np.quantile(means,[.025,.975]))
