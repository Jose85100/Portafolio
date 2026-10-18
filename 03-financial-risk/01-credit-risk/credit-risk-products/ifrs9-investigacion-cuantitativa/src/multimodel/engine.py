"""Monthly component ECL and funded Stage 3; explicit scenario and model lineage."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .contracts import array, frame, integer, probabilities, weights
from ..ifrs9_engine import credit_impaired_shortfall


@dataclass(frozen=True)
class Scenario:
    name: str
    weight: float
    macro: tuple
    recovery_multiplier: float = 1.
    recovery_delay_years: float = 0.

    def validate(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError('Scenario name required')
        probabilities([self.weight], 'scenario weight'); array(self.macro, 'macro')
        if not np.isfinite([self.recovery_multiplier, self.recovery_delay_years]).all() or self.recovery_multiplier < 0 or self.recovery_delay_years < 0:
            raise ValueError('Nonnegative recovery multiplier and delay required')


def component_ecl(marginal_pd, lgd, ead, eir, stages):
    """Return per-loan ECL12, lifetime and selected; month-end default convention.

    Stage 1 truncates DEFAULT EVENTS at month 12. LGD at default already contains
    the entire subsequent recovery shortfall. It is not a truncation of recoveries.
    """
    mass = probabilities(marginal_pd, 'marginal PD', 2)
    loss = probabilities(lgd, 'LGD', 2); exposure = array(ead, 'EAD', 2)
    rates = array(eir, 'annual EIR'); s = array(stages, 'stages')
    n, h = mass.shape
    if loss.shape != mass.shape or exposure.shape != mass.shape or len(rates) != n or len(s) != n:
        raise ValueError('Component dimensions must match')
    if (exposure < 0).any() or (rates <= -1).any() or not np.isin(s, [1, 2]).all() or (mass.sum(axis=1) > 1+1e-12).any():
        raise ValueError('Invalid exposure, EIR, stage or total first-default probability')
    with np.errstate(over='raise', invalid='raise'):
        discount = np.exp(-np.log1p(rates)[:, None]*np.arange(1, h+1)/12)
        contributions = mass*loss*exposure*discount
        e12 = contributions[:, :12].sum(axis=1); lifetime = contributions.sum(axis=1)
    if not np.isfinite(lifetime).all():
        raise ArithmeticError('Nonfinite ECL')
    return e12, lifetime, np.where(s == 1, e12, lifetime), contributions


def run_ecl(loans, pd_model, lgd_model, ead_model, scenarios):
    frame(loans, ['eir', 'stage', 'balance'])
    if 'loan_id' not in loans or loans.loan_id.isna().any() or not loans.loan_id.is_unique:
        raise ValueError('Unique nonnull loan_id required')
    if (loans.eir <= -1).any() or (loans.balance < 0).any() or not np.isin(loans.stage, [1, 2, 3]).all():
        raise ValueError('Invalid EIR, balance or stage')
    scenarios = tuple(scenarios)
    for scenario in scenarios:
        scenario.validate()
    if len({s.name for s in scenarios}) != len(scenarios):
        raise ValueError('Duplicate scenario names')
    weights({s.name:s.weight for s in scenarios})
    horizons = {len(s.macro) for s in scenarios}
    if len(horizons) != 1:
        raise ValueError('All scenarios require the same horizon')
    horizon = integer(next(iter(horizons)), 'horizon')
    if 'term_months' not in loans or (loans.term_months > horizon).any():
        raise ValueError('Scenario horizon must cover every remaining contractual term')
    records = []; details = []
    for scenario in scenarios:
        live = loans.stage.ne(3); p = loans.loc[live]
        if len(p):
            mass = probabilities(pd_model.predict_curve(p, scenario.macro), 'model marginal PD', 2)
            if mass.shape != (len(p), horizon):
                raise ValueError('PD model must return exactly one curve per input loan')
            ead = ead_model.predict(p, scenario.macro); lgd = lgd_model.predict(p, scenario.macro, ead)
            # Term expiry applies to both EAD and first-default mass.
            months = np.arange(1, horizon+1)
            mass = np.where(months <= p.term_months.to_numpy()[:, None], mass, 0.)
            e12, lifetime, selected, contributions = component_ecl(mass, lgd, ead, p.eir, p.stage)
            for i, row in enumerate(p.itertuples()):
                records.append(dict(loan_id=row.loan_id, scenario=scenario.name, weight=scenario.weight,
                    stage=row.stage, ecl_12m=e12[i], ecl_lifetime=lifetime[i], ecl=selected[i], basis='monthly_components'))
                for month in range(int(row.term_months)):
                    details.append(dict(loan_id=row.loan_id, scenario=scenario.name, month=month+1,
                        marginal_pd=mass[i, month], lgd=lgd[i, month], ead=ead[i, month],
                        contribution=contributions[i, month], selected=bool(row.stage == 2 or month < 12)))
        for row in loans.loc[~live].itertuples():
            if not all(hasattr(row, name) for name in ['recovery_cashflows', 'recovery_times']):
                raise ValueError('Stage 3 requires explicit net recovery cashflows and times')
            flows = array(row.recovery_cashflows, 'recoveries')*scenario.recovery_multiplier
            times = array(row.recovery_times, 'recovery times') + scenario.recovery_delay_years
            result = credit_impaired_shortfall(row.balance, flows, times, row.eir)
            records.append(dict(loan_id=row.loan_id, scenario=scenario.name, weight=scenario.weight,
                stage=3, ecl_12m=np.nan, ecl_lifetime=np.nan, ecl=result['ecl'], basis='funded_recovery_cashflows'))
    by_scenario = pd.DataFrame(records)
    by_scenario['weighted_ecl'] = by_scenario.ecl*by_scenario.weight
    portfolio = by_scenario.groupby('loan_id', sort=False).agg(ecl=('weighted_ecl', 'sum'), stage=('stage', 'first'))
    portfolio = portfolio.reindex(loans.loan_id)
    portfolio.index.name = 'loan_id'
    if not np.isfinite(portfolio.ecl).all():
        raise ArithmeticError('Nonfinite aggregated ECL')
    lineage = {'pd': pd_model.model_id, 'lgd': lgd_model.model_id, 'ead': ead_model.model_id}
    return {'loans':portfolio, 'scenarios':by_scenario, 'monthly':pd.DataFrame(details), 'models':lineage}


class ProvisionMatrix:
    """Separate simplified lifetime loss-rate experiment for trade receivables.

    Fits completed cohort cash shortfalls / opening exposure, by aging bucket.
    No migration from bank loan PDs; no claim of eligibility for any instrument.
    """
    def fit(self, completed):
        frame(completed, ['exposure', 'discounted_shortfall'])
        if 'bucket' not in completed or completed.bucket.isna().any() or (completed.exposure <= 0).any() or (completed.discounted_shortfall < 0).any() or (completed.discounted_shortfall > completed.exposure).any():
            raise ValueError('Completed cohorts need valid buckets/exposure/shortfall')
        g = completed.groupby('bucket')[['exposure', 'discounted_shortfall']].sum()
        self.rates = g.discounted_shortfall/g.exposure
        return self

    def predict(self, receivables, scenario_multipliers):
        frame(receivables, ['exposure'])
        if 'bucket' not in receivables or not receivables.bucket.isin(self.rates.index).all() or (receivables.exposure < 0).any():
            raise ValueError('Known buckets and nonnegative exposure required')
        weights({k:v[0] for k,v in scenario_multipliers.items()})
        result = np.zeros(len(receivables))
        for weight, multiplier in scenario_multipliers.values():
            if not np.isfinite(multiplier) or multiplier < 0:
                raise ValueError('Nonnegative finite loss-rate multiplier required')
            result += weight*np.clip(receivables.bucket.map(self.rates).to_numpy()*multiplier, 0, 1)*receivables.exposure
        return result
