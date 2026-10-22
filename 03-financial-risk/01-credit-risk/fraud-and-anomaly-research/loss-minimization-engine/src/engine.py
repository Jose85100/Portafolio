"""Research-only loss engine: finite contracts, temporal features and MILP policies.

Money is COP, effort is reviewer-minutes. Independent cases; no denial action.
Effectiveness is an explicit assumption, not an estimated causal effect.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint


def finite(value, name, low=0.0, high=math.inf):
    if isinstance(value, bool) or not isinstance(value, (int, float, np.number)):
        raise ValueError(f'{name}: numeric scalar required')
    value = float(value)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name}: finite value in [{low}, {high}] required')
    return value


@dataclass(frozen=True)
class Case:
    case_id: str
    probability: float
    loss_cop: float

    def __post_init__(self):
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError('non-empty case_id required')
        finite(self.probability, 'probability', high=1)
        finite(self.loss_cop, 'loss_cop')


@dataclass(frozen=True)
class Action:
    name: str
    prevent_fraction: float
    cost_cop: float
    legitimate_friction_cop: float
    effort_minutes: float

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('action name required')
        finite(self.prevent_fraction, 'prevent_fraction', high=1)
        for key in ('cost_cop', 'legitimate_friction_cop', 'effort_minutes'):
            finite(getattr(self, key), key)


@dataclass(frozen=True)
class Scenario:
    name: str
    probability_multiplier: float = 1.0
    severity_multiplier: float = 1.0
    effectiveness_multiplier: float = 1.0

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError('scenario name required')
        for key in ('probability_multiplier', 'severity_multiplier', 'effectiveness_multiplier'):
            finite(getattr(self, key), key)


def expected_cost(case, action, scenario=Scenario('base')):
    """Fraud loss remaining + action cost + friction on legitimate applicants."""
    p = min(1.0, case.probability * scenario.probability_multiplier)
    q = min(1.0, action.prevent_fraction * scenario.effectiveness_multiplier)
    value = (p * case.loss_cop * scenario.severity_multiplier * (1 - q)
             + action.cost_cop + (1 - p) * action.legitimate_friction_cop)
    return finite(value, 'expected_cost')


def shared_entity_count(links, entity, cutoff, exclude_application=None, window=30.):
    """Count distinct previous applications in [cutoff-window, cutoff).

    Both event and availability times must precede the decision; current case is
    excluded. Synthetic scalar time is days. Duplicate links are idempotent.
    """
    finite(cutoff, 'cutoff')
    finite(window, 'window')
    observed = set()
    for link in links:
        for field in ('event_at', 'available_at'):
            finite(link[field], field)
        if (link['entity'] == entity and link['application_id'] != exclude_application
                and cutoff-window <= link['event_at'] < cutoff
                and link['available_at'] <= cutoff):
            observed.add(link['application_id'])
    return len(observed)


def optimize(cases, actions, capacity_minutes, scenarios=None, weights=None,
             objective='expected'):
    """Choose exactly one action per independent case via binary MILP.

    expected: minimize weighted scenario cost; worst_case: minimize largest total
    scenario cost (finite scenario minimax, not distributionally robust CVaR).
    Costs are scaled by 1e6 for numerical conditioning. No rounding of money.
    """
    capacity = finite(capacity_minutes, 'capacity_minutes')
    if objective not in ('expected', 'worst_case'):
        raise ValueError('objective must be expected or worst_case')
    scenarios = [Scenario('base')] if scenarios is None else list(scenarios)
    if not cases or not actions or not scenarios:
        raise ValueError('cases, actions and scenarios must be non-empty')
    if len({c.case_id for c in cases}) != len(cases):
        raise ValueError('deduplicate cases before optimization')
    if len({a.name for a in actions}) != len(actions):
        raise ValueError('action names must be unique')
    if len({s.name for s in scenarios}) != len(scenarios):
        raise ValueError('scenario names must be unique')
    if not any(a.name == 'allow' and a.prevent_fraction == 0 and a.cost_cop == 0
               and a.legitimate_friction_cop == 0 and a.effort_minutes == 0
               for a in actions):
        raise ValueError('a free, zero-effect allow action is required')
    if weights is None:
        weights = [1 / len(scenarios)] * len(scenarios)
    w = np.array([finite(v, 'weight', high=1) for v in weights])
    if len(w) != len(scenarios) or not math.isclose(float(w.sum()), 1, abs_tol=1e-10):
        raise ValueError('scenario weights must have matching size and sum to one')
    n, m = len(cases), len(actions)
    k = n*m
    matrix = np.array([[expected_cost(c,a,s) for c in cases for a in actions]
                       for s in scenarios])
    effort = np.tile([a.effort_minutes for a in actions], n)
    extra = int(objective == 'worst_case')
    width = k + extra
    equality = np.zeros((n, width))
    for i in range(n):
        equality[i, i*m:(i+1)*m] = 1
    rows = [*equality, np.r_[effort, np.zeros(extra)]]
    lower = [*np.ones(n), -np.inf]
    upper = [*np.ones(n), capacity]
    if extra:
        for cost in matrix:
            rows.append(np.r_[cost/1e6, -1])
            lower.append(-np.inf)
            upper.append(0)
        coefficients = np.r_[np.zeros(k), 1.]
    else:
        coefficients = w @ matrix / 1e6
    result = milp(c=coefficients,
                  integrality=np.r_[np.ones(k), np.zeros(extra)],
                  bounds=Bounds(np.zeros(width), np.r_[np.ones(k), np.full(extra,np.inf)]),
                  constraints=LinearConstraint(np.array(rows), lower, upper),
                  options={'mip_rel_gap': 0., 'time_limit': 30.})
    if result.status != 0 or result.x is None:
        raise RuntimeError(f'No optimal MILP certificate: {result.message}')
    chosen = np.argmax(result.x[:k].reshape(n,m), axis=1)
    selected = np.zeros(k)
    selected[np.arange(n)*m + chosen] = 1
    if np.max(np.abs(result.x[:k]-selected)) > 1e-6:
        raise RuntimeError('non-integral solution')
    used = float(effort @ selected)
    if used > capacity + 1e-6:
        raise RuntimeError('capacity violated')
    costs = matrix @ selected
    value = float(costs.max() if extra else w @ costs)
    if not np.isclose(value/1e6, result.fun, atol=1e-7, rtol=1e-7):
        raise RuntimeError('objective reconciliation failed')
    return {'case_ids': [c.case_id for c in cases],
            'actions': [actions[j].name for j in chosen],
            'effort_minutes': used, 'scenario_costs_cop': dict(zip([s.name for s in scenarios], costs.tolist())),
            'objective_cop': value, 'solver_status': int(result.status),
            'mip_gap': float(result.mip_gap), 'objective_type': objective}
