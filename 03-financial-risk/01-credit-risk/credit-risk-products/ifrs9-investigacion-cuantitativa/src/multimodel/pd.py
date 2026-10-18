"""Three fitted PD alternatives with a common monthly first-default mass interface."""
import numpy as np
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from .contracts import array, default_curve, frame, integer, probabilities


def _fit(x, y, regularization):
    x = array(x, 'features', 2); y = probabilities(y, 'default')
    if len(x) != len(y) or not np.isin(y, [0, 1]).all() or len(np.unique(y)) != 2:
        raise ValueError('Both binary outcome classes and aligned features required')
    if not np.isfinite(regularization) or regularization <= 0:
        raise ValueError('Positive regularization required')
    return LogisticRegression(C=regularization, max_iter=1000, random_state=19).fit(x, y)


def _inputs(loans, macro):
    frame(loans, ['score', 'segment', 'age_months'])
    if not np.isin(loans.segment, [0, 1]).all() or (loans.age_months < 0).any():
        raise ValueError('Binary segment and nonnegative age required')
    return array(macro, 'monthly macro path')


class LogisticPD:
    """12m logit; constant-hazard annual-to-monthly conversion, with macro odds shift.

    Training includes only fully observed 12-month horizons. Future monthly macro
    values adjust the logit; extending that hazard beyond 12m is an extrapolation.
    """
    model_id = 'pd_logit_12m'

    def fit(self, cohort, regularization=1.):
        frame(cohort, ['score', 'segment', 'macro', 'default_12m'])
        self.estimator = _fit(cohort[['score', 'segment', 'macro']], cohort.default_12m, regularization)
        return self

    def predict_curve(self, loans, macro):
        path = _inputs(loans, macro)
        x = np.column_stack([loans.score, loans.segment, np.zeros(len(loans))])
        intercept = self.estimator.decision_function(x)
        logits = intercept[:, None] + self.estimator.coef_[0, 2]*path[None, :]
        annual = expit(logits)
        q = -np.expm1(np.log1p(-np.minimum(annual, np.nextafter(1., 0.)))/12)
        return default_curve(q)[0]


class SurvivalPD:
    """Pooled monthly discrete-time logistic hazard, conditional on still at risk."""
    model_id = 'pd_monthly_survival'

    @staticmethod
    def features(score, segment, macro, age):
        return np.column_stack([score, segment, macro, np.log1p(age)/4])

    def fit(self, panel, regularization=1.):
        frame(panel, ['score', 'segment', 'macro', 'age_months', 'default'])
        # Caller supplies only at-risk rows, with at most one terminal default.
        if {'loan_id', 'month'}-set(panel):
            raise ValueError('Survival panel needs loan_id and month')
        if (panel.month < 1).any() or (panel.month != np.floor(panel.month)).any() or panel.loan_id.isna().any():
            raise ValueError('Positive integer months and nonnull loan IDs required')
        if panel.duplicated(['loan_id', 'month']).any():
            raise ValueError('Duplicate loan-month')
        for _, group in panel.groupby('loan_id', sort=False):
            g = group.sort_values('month')
            if (g.age_months != np.floor(g.age_months)).any() or (np.diff(g.month) != 1).any() or (np.diff(g.age_months) != 1).any():
                raise ValueError('Consecutive at-risk months and integer ages required')
            if (g.age_months < 0).any() or g.default.sum() > 1 or (g.default.iloc[:-1] != 0).any():
                raise ValueError('Invalid at-risk panel: default must be terminal')
        x = self.features(panel.score, panel.segment, panel.macro, panel.age_months)
        self.estimator = _fit(x, panel.default, regularization)
        return self

    def predict_curve(self, loans, macro):
        path = _inputs(loans, macro); n, h = len(loans), len(path)
        age = loans.age_months.to_numpy()[:, None] + np.arange(h)
        x = self.features(np.repeat(loans.score, h), np.repeat(loans.segment, h),
                          np.tile(path, n), age.ravel())
        q = self.estimator.predict_proba(x)[:, 1].reshape(n, h)
        return default_curve(q)[0]


class TransitionPD:
    """Monthly homogeneous Markov ratings, final state absorbing default.

    Laplace smoothing is explicit; default stays absorbing. Scenario macro shifts
    default odds in each live row with a supplied (not estimated) coefficient.
    """
    model_id = 'pd_rating_transitions'

    def fit(self, transitions, n_states=4, smoothing=.5, macro_beta=.35):
        integer(n_states, 'n_states', 20)
        if n_states < 2 or not np.isfinite(smoothing) or smoothing < 0 or not np.isfinite(macro_beta):
            raise ValueError('Invalid Markov parameters')
        frame(transitions, ['from_state', 'to_state'])
        a = transitions[['from_state', 'to_state']].to_numpy()
        if (a != np.floor(a)).any() or ((a < 0) | (a >= n_states)).any():
            raise ValueError('Invalid rating states')
        if ((a[:, 0] == n_states-1) & (a[:, 1] != n_states-1)).any():
            raise ValueError('Default must be absorbing')
        counts = np.full((n_states, n_states), smoothing)
        np.add.at(counts, (a[:, 0].astype(int), a[:, 1].astype(int)), 1.)
        if (counts[:-1].sum(axis=1) == 0).any():
            raise ValueError('Unobserved live rating requires positive smoothing')
        counts[-1] = 0; counts[-1, -1] = 1
        self.matrix = counts/counts.sum(axis=1)[:, None]
        self.macro_beta = float(macro_beta)
        return self

    def predict_curve(self, loans, macro):
        path = array(macro, 'monthly macro path'); frame(loans, ['rating'])
        r = loans.rating.to_numpy(); k = len(self.matrix)
        if (r != np.floor(r)).any() or ((r < 0) | (r >= k-1)).any():
            raise ValueError('Only live integer ratings accepted')
        state = np.eye(k)[r.astype(int)]; marginal = np.zeros((len(r), len(path)))
        for month, macro_value in enumerate(path):
            p = self.matrix.copy(); old = p[:-1, -1]
            shifted = expit(logit(np.clip(old, 1e-15, 1-1e-15)) + self.macro_beta*macro_value)
            # Exact boundary rows remain exact; no resurrection of zero probabilities.
            shifted = np.where(old == 0, 0., np.where(old == 1, 1., shifted))
            scale = np.divide(1-shifted, 1-old, out=np.zeros_like(old), where=old < 1)
            p[:-1, :-1] *= scale[:, None]; p[:-1, -1] = shifted
            marginal[:, month] = state[:, :-1] @ p[:-1, -1]
            state = state @ p
        return marginal
