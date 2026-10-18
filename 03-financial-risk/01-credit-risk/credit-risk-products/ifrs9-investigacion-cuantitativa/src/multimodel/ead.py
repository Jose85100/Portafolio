"""Beginning-of-month exposure conditional on no prior default. No survival factor."""
import numpy as np
from .contracts import frame, integer, probabilities
from .lgd import FractionalLogit


def annuity_exposure(balance, annual_coupon, term_months, horizon, annual_cpr=0.):
    integer(term_months, 'term_months'); integer(horizon, 'horizon')
    if not np.isfinite([balance, annual_coupon, annual_cpr]).all() or balance < 0 or annual_coupon < 0 or not 0 <= annual_cpr <= 1:
        raise ValueError('Nonnegative balance/coupon and CPR in [0,1] required')
    monthly = np.expm1(np.log1p(annual_coupon)/12)
    payment = balance/term_months if monthly == 0 else balance*monthly/(-np.expm1(-term_months*np.log1p(monthly)))
    exposure = np.zeros(horizon); outstanding = float(balance)
    retention = (1-annual_cpr)**(1/12)
    for m in range(min(horizon, term_months)):
        exposure[m] = outstanding*retention**m
        outstanding = max(outstanding*(1+monthly)-payment, 0.)
    if not np.isfinite(exposure).all():
        raise ArithmeticError('Nonfinite amortization')
    return exposure


class CCFModel:
    """CCF fitted on completed default windows with positive opening undrawn limit."""
    model_id = 'ead_fractional_ccf'

    def fit(self, windows):
        frame(windows, ['utilization', 'segment', 'macro', 'ccf'])
        probabilities(windows.utilization, 'utilization')
        if not np.isin(windows.segment, [0, 1]).all():
            raise ValueError('Binary segment required')
        self.regression = FractionalLogit().fit(windows[['utilization', 'segment', 'macro']], windows.ccf)
        return self

    def predict(self, utilization, segment, macro):
        probabilities(utilization, 'utilization')
        if not np.isin(segment, [0, 1]).all():
            raise ValueError('Binary segment required')
        return self.regression.predict(np.column_stack([utilization, segment, macro]))


class ExposureModel:
    """Mixed portfolio adapter: annuity (+optional CPR), revolver (+fixed/fitted CCF)."""
    def __init__(self, annual_cpr=0., fixed_ccf=.5, ccf_model=None):
        probabilities([annual_cpr, fixed_ccf])
        self.annual_cpr = float(annual_cpr); self.fixed_ccf = float(fixed_ccf); self.ccf_model = ccf_model
        self.model_id = 'ead_contractual_fixed_ccf' if ccf_model is None and annual_cpr == 0 else 'ead_prepayment_fitted_ccf'

    def predict(self, loans, macro):
        path = np.asarray(macro, dtype=float); integer(len(path), 'horizon')
        if path.ndim != 1 or not np.isfinite(path).all():
            raise ValueError('Finite monthly macro path required')
        frame(loans, ['balance', 'limit', 'coupon', 'term_months', 'segment'])
        if 'product' not in loans or not loans['product'].isin(['term', 'revolver']).all():
            raise ValueError('Products must be term or revolver')
        if (loans.balance < 0).any() or (loans['limit'] < loans.balance).any():
            raise ValueError('Require 0 <= balance <= limit')
        out = np.zeros((len(loans), len(path)))
        for i, (_, row) in enumerate(loans.iterrows()):
            term = integer(row.term_months, 'term_months'); h = min(term, len(path))
            if row['product'] == 'term':
                out[i] = annuity_exposure(row.balance, row.coupon, term, len(path), self.annual_cpr)
            else:
                u = row.balance/row['limit'] if row['limit'] else 0.
                ccf = (self.ccf_model.predict(np.full(h, u), np.full(h, row.segment), path[:h])
                       if self.ccf_model else np.full(h, self.fixed_ccf))
                out[i, :h] = row.balance + (row['limit']-row.balance)*ccf
        return out
