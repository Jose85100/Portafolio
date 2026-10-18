"""Workout-based LGD; loss is valued at default, then ECL discounts to reporting."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from .contracts import array, frame, probabilities


class FractionalLogit:
    """Penalized Bernoulli quasi-likelihood for bounded continuous responses.

    Endpoint targets 0 and 1 are valid. This is conditional mean regression, not a
    beta likelihood, and coefficient uncertainty is not estimated here.
    """
    def fit(self, x, y, penalty=.01):
        x = array(x, 'features', 2); y = probabilities(y, 'fractional target')
        if len(x) != len(y) or not np.isfinite(penalty) or penalty <= 0:
            raise ValueError('Aligned targets and positive penalty required')
        self.location = x.mean(axis=0); self.scale = x.std(axis=0)
        self.scale[self.scale < 1e-12] = 1
        z = np.column_stack([np.ones(len(x)), (x-self.location)/self.scale])
        def objective(b):
            eta = z @ b
            value = np.mean(np.logaddexp(0, eta)-y*eta) + penalty*np.dot(b[1:], b[1:])/2
            gradient = z.T @ (expit(eta)-y)/len(y)
            gradient[1:] += penalty*b[1:]
            return value, gradient
        result = minimize(objective, np.zeros(z.shape[1]), jac=True, method='L-BFGS-B',
                          options={'maxiter': 1000, 'ftol': 1e-12, 'gtol': 1e-8})
        if not result.success or not np.isfinite(result.x).all():
            raise ArithmeticError('Fractional logit fit failed: '+result.message)
        self.coefficients = result.x
        return self

    def predict(self, x):
        x = array(x, 'features', 2)
        if x.shape[1] != len(self.location):
            raise ValueError('Feature dimension mismatch')
        z = np.column_stack([np.ones(len(x)), (x-self.location)/self.scale])
        return expit(z @ self.coefficients)


class SegmentLGD:
    model_id = 'lgd_segment_workout'

    def fit(self, workouts):
        frame(workouts, ['segment', 'loss_fraction'])
        probabilities(workouts.loss_fraction)
        if not np.isin(workouts.segment, [0, 1]).all() or set(workouts.segment) != {0, 1}:
            raise ValueError('Both portfolio segments need observations')
        # Account-weighted conditional mean, not exposure-weighted aggregate ratio.
        self.means = workouts.groupby('segment').loss_fraction.mean().to_dict()
        return self

    def predict(self, loans, macro, ead):
        frame(loans, ['segment'])
        if not np.isin(loans.segment, list(self.means)).all():
            raise ValueError('Unknown segment')
        return np.broadcast_to(loans.segment.map(self.means).to_numpy()[:, None], ead.shape).copy()


class RegressionLGD:
    model_id = 'lgd_fractional_workout'

    def fit(self, workouts):
        frame(workouts, ['collateral_ratio', 'segment', 'macro', 'loss_fraction'])
        if (workouts.collateral_ratio < 0).any() or not np.isin(workouts.segment, [0, 1]).all():
            raise ValueError('Nonnegative collateral ratio and binary segment required')
        self.regression = FractionalLogit().fit(workouts[['collateral_ratio', 'segment', 'macro']], workouts.loss_fraction)
        return self

    def predict(self, loans, macro, ead):
        frame(loans, ['collateral_ratio', 'segment']); path = array(macro, 'macro')
        if (loans.collateral_ratio < 0).any() or not np.isin(loans.segment, [0, 1]).all():
            raise ValueError('Nonnegative collateral ratio and binary segment required')
        n, h = ead.shape
        if len(path) != h or len(loans) != n:
            raise ValueError('LGD shape mismatch')
        x = np.column_stack([np.repeat(loans.collateral_ratio, h), np.repeat(loans.segment, h), np.tile(path, n)])
        return self.regression.predict(x).reshape(n, h)


class CashflowLGD:
    """Net recovery schedule at default; EIR discounting captures recovery delay.

    Collateral recovery and unsecured recovery are separate, bounded assumptions.
    Costs enter as a haircut to recoveries. No new EAD is inferred from future PD.
    """
    model_id = 'lgd_recovery_cashflows'

    def __init__(self, haircut=.25, cost_rate=.08, unsecured_rate=.15,
                 recovery_years=(1., 2., 3.), recovery_weights=(.5, .3, .2)):
        p = probabilities([haircut, cost_rate, unsecured_rate]); self.haircut, self.cost_rate, self.unsecured_rate = p
        self.times = array(recovery_years, 'recovery times')
        self.weights = probabilities(recovery_weights, 'recovery weights')
        if self.times.shape != self.weights.shape or (self.times < 0).any() or (np.diff(self.times) <= 0).any() or not np.isclose(self.weights.sum(), 1, rtol=0, atol=1e-12):
            raise ValueError('Ordered recovery dates and weights summing to one required')

    def predict(self, loans, macro, ead):
        frame(loans, ['collateral_ratio', 'eir']); path = array(macro, 'macro')
        if (loans.collateral_ratio < 0).any() or (loans.eir <= -1).any() or ead.shape != (len(loans), len(path)):
            raise ValueError('Invalid cashflow LGD inputs')
        stress = np.exp(np.clip(-.12*path, -50, 50))
        secured = np.minimum(loans.collateral_ratio.to_numpy()[:, None]*(1-self.haircut)*stress, 1.)
        net_fraction = (secured + (1-secured)*self.unsecured_rate)*(1-self.cost_rate)
        pv = (np.exp(-np.log1p(loans.eir.to_numpy())[:, None]*self.times)*self.weights).sum(axis=1)
        return np.clip(1-net_fraction*pv[:, None], 0, 1)
