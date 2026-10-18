"""Transparent policy experiment; thresholds are configurable, not IFRS mandates."""
import numpy as np
import pandas as pd
from .contracts import frame, probabilities


def classify(loans, ratio_threshold=2., absolute_threshold=.02, watchlist=True):
    frame(loans, ['origin_lifetime_pd', 'current_lifetime_pd', 'dpd'])
    if 'credit_impaired' not in loans or 'watchlist' not in loans:
        raise ValueError('Explicit credit_impaired and watchlist flags required')
    if not loans.credit_impaired.isin([True, False]).all() or not loans.watchlist.isin([True, False]).all():
        raise ValueError('Boolean flags required')
    old = probabilities(loans.origin_lifetime_pd); new = probabilities(loans.current_lifetime_pd)
    if not np.isfinite([ratio_threshold, absolute_threshold]).all() or ratio_threshold <= 1 or not 0 <= absolute_threshold <= 1:
        raise ValueError('Invalid SICR policy thresholds')
    if (loans.dpd < 0).any() or (loans.dpd != np.floor(loans.dpd)).any():
        raise ValueError('Nonnegative integral DPD required')
    # Same remaining horizon and consistent model definition must be used by caller.
    ratio = np.divide(new, old, out=np.full(len(old), np.inf), where=old > 0)
    ratio[(old == 0) & (new == 0)] = 1.
    quantitative = (ratio >= ratio_threshold) & (new-old >= absolute_threshold)
    impaired = loans.credit_impaired.to_numpy(bool) | (loans.dpd.to_numpy() >= 90)
    significant = quantitative | (loans.dpd.to_numpy() >= 30)
    if watchlist:
        significant |= loans.watchlist.to_numpy(bool)
    stage = np.select([impaired, significant], [3, 2], default=1)
    reason = np.select([impaired, loans.dpd.to_numpy() >= 30,
                        loans.watchlist.to_numpy(bool) & watchlist, quantitative],
                       ['credit_impaired_or_90dpd', '30dpd_backstop', 'watchlist', 'relative_and_absolute_pd'], default='no_trigger')
    return pd.DataFrame({'stage': stage, 'stage_reason': reason}, index=loans.index)
