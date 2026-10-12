"""Finite-horizon investment timing under a binomial demand process."""
from dataclasses import dataclass
from math import exp, isfinite

@dataclass(frozen=True)
class InvestmentCase:
    present_value: float
    investment_cost: float
    up: float
    down: float
    up_probability: float
    discount_rate: float
    periods: int

    def validate(self):
        values = (self.present_value, self.investment_cost, self.up, self.down,
                  self.up_probability, self.discount_rate)
        if not all(isfinite(x) for x in values):
            raise ValueError("all inputs must be finite")
        if self.present_value < 0 or self.investment_cost < 0:
            raise ValueError("cash values cannot be negative")
        if self.up < 1 or not 0 < self.down <= 1 or self.up <= self.down:
            raise ValueError("expected 0 < down <= 1 <= up and up > down")
        if not 0 <= self.up_probability <= 1 or self.discount_rate < 0:
            raise ValueError("invalid probability or discount rate")
        if not isinstance(self.periods, int) or not 0 <= self.periods <= 100:
            raise ValueError("periods must be between 0 and 100")

def solve(case: InvestmentCase):
    """Risk-adjusted physical expectation; discount rate supplied by the analyst.

    A cash-flow valuation tree is not a risk-neutral option price. The investor
    can invest once; after exercise the payoff is PV minus investment cost.
    """
    case.validate()
    disc = exp(-case.discount_rate)
    values = [max(case.present_value * case.up**k *
                  case.down**(case.periods-k) - case.investment_cost, 0.0)
              for k in range(case.periods+1)]
    root_action = "wait"
    for t in range(case.periods-1, -1, -1):
        next_values = []
        for k in range(t+1):
            project_pv = case.present_value * case.up**k * case.down**(t-k)
            exercise = max(project_pv - case.investment_cost, 0.0)
            wait = disc * (case.up_probability * values[k+1] +
                           (1-case.up_probability) * values[k])
            if t == 0:
                root_action = "invest" if exercise >= wait and exercise > 0 else "wait"
            next_values.append(max(exercise, wait))
        values = next_values
    if case.periods == 0:
        root_action = "invest" if values[0] > 0 else "reject"
    return {"option_value": values[0], "immediate_npv":
            case.present_value-case.investment_cost, "action": root_action}
