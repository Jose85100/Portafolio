"""Exact assumed-box experiment; LP has inequality marginal constraints."""
import json
from itertools import product
from pathlib import Path
import platform
from statistics import median
import time
import tracemalloc
import numpy as np
import scipy
from scipy.optimize import linprog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from benchmarks.joint_role_run import save
from src.interval_role import ProbabilityInterval as PI, IntervalPlan, interval_bounds, select_interval
from src.joint_role import joint_bounds, select_joint
from src.reserve_ambiguity import ReservePlan


def lp_bounds(plan, risk, shock, upper=False):
    states = np.array(list(product((0, 1), repeat=3)))
    s = shock.lower if upper else shock.upper
    objective = (1-s)*states[:, 0] + s*np.all(states == 1, axis=1)
    if upper:
        objective = -objective
    a = states.T
    marginals = (risk, plan.q1, plan.q2)
    result = linprog(objective, A_ub=np.vstack((a, -a)),
                     b_ub=[x.upper for x in marginals]+[-x.lower for x in marginals],
                     A_eq=np.ones((1, 8)), b_eq=[1], bounds=(0, None), method='highs')
    assert result.success, result.message
    return (-result.fun if upper else result.fun), result.x, states


def load_config():
    cfg = json.loads((Path(__file__).resolve().parents[1]/'config_intervals.json').read_text())
    plans = [IntervalPlan(x['name'], PI(*x['q1']), PI(*x['q2']), x['cost']) for x in cfg['plans']]
    return cfg, plans, PI(*cfg['risk']), PI(*cfg['shock'])


def point_baseline(plans, risk, shock, target):
    r = (risk.lower+risk.upper)/2
    s = (shock.lower+shock.upper)/2
    points = [ReservePlan(p.name, (p.q1.lower+p.q1.upper)/2,
                          (p.q2.lower+p.q2.upper)/2, p.cost) for p in plans]
    try:
        selected = select_joint(points, target, s, r).name
    except ValueError:
        selected = 'infeasible'
    return points, r, s, selected


def main():
    root = Path(__file__).resolve().parents[1]
    cfg, plans, risk, shock = load_config()
    points, rcenter, scenter, point_selection = point_baseline(plans, risk, shock, cfg['target'])
    rows = []
    witnesses = []
    for p, point in zip(plans, points):
        b = interval_bounds(p, risk, shock)
        lo, witness, states = lp_bounds(p, risk, shock)
        hi, _, _ = lp_bounds(p, risk, shock, True)
        rows.append({'plan': p.name, 'cost': p.cost, 'point_lower31': joint_bounds(point, scenter, rcenter)['lower'],
                     **b, 'lp_lower': lo, 'lp_upper': hi})
        for state, mass in zip(states, witness):
            witnesses.append({'plan': p.name, 'R': state[0], 'B1': state[1], 'B2': state[2], 'mass': mass})
    save(root/'results/interval_plans.csv', rows)
    save(root/'results/interval_witnesses.csv', witnesses)
    grid = []
    intervals = [PI(0, 0), PI(.2, .8), PI(1, 1)]
    for r, q1, q2, s in product(intervals, repeat=4):
        p = IntervalPlan('p', q1, q2, 0)
        b = interval_bounds(p, r, s)
        lo, _, _ = lp_bounds(p, r, s)
        hi, _, _ = lp_bounds(p, r, s, True)
        grid.append({'r_lo': r.lower, 'r_hi': r.upper, 'q1_lo': q1.lower, 'q1_hi': q1.upper,
                     'q2_lo': q2.lower, 'q2_hi': q2.upper, 's_lo': s.lower, 's_hi': s.upper,
                     'lower': b['lower'], 'upper': b['upper'], 'lp_lower': lo, 'lp_upper': hi,
                     'max_error': max(abs(b['lower']-lo), abs(b['upper']-hi))})
    save(root/'results/interval_oracle.csv', grid)
    sensitivity = []
    for i in range(101):
        a = i/100
        q = PI(.8-.02*a, .8+.02*a)
        b = interval_bounds(IntervalPlan('B', q, q, 3), PI(.95-.01*a, .95+.01*a), PI(.2-.01*a, .2+.01*a))
        sensitivity.append({'width_fraction': a, **b})
    save(root/'results/interval_sensitivity.csv', sensitivity)
    lp_bounds(plans[1], risk, shock)
    perf = []
    for n in (1, 10, 100):
        for method in ('closed', 'lp8_intervals'):
            for rep in range(5):
                tracemalloc.start()
                tick = time.perf_counter()
                for _ in range(n):
                    if method == 'closed':
                        interval_bounds(plans[1], risk, shock)
                    else:
                        lp_bounds(plans[1], risk, shock)
                elapsed = time.perf_counter()-tick
                peak = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                perf.append({'n': n, 'method': method, 'repeat': rep, 'seconds': elapsed, 'python_peak_bytes': peak})
    save(root/'results/interval_performance.csv', perf)
    summary = {'selected_interval': select_interval(plans, risk, shock, cfg['target']).name,
               'target': cfg['target'], 'oracle_boxes': len(grid), 'lp_objectives': 2*len(grid),
               'max_error': max(x['max_error'] for x in grid), 'plans': rows,
               'point_selection': point_selection, 'coverage_claim': 'none: assumed deterministic boxes, no observed data',
               'timing_n100_median_seconds': {m: median(x['seconds'] for x in perf if x['n'] == 100 and x['method'] == m)
                                           for m in ('closed', 'lp8_intervals')},
               'python': platform.python_version(), 'platform': platform.platform(), 'processor': platform.processor(),
               'numpy': np.__version__, 'scipy': scipy.__version__, 'memory_scope': 'tracemalloc Python only, not native HiGHS/RSS',
               'seed': None, 'source': cfg['source']}
    (root/'results/interval_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    x = np.arange(3)
    axes[0].bar(x-.15, [r['point_lower31'] for r in rows], .3, label='Point31', hatch='//')
    axes[0].bar(x+.15, [r['lower'] for r in rows], .3, label='Assumed box', hatch='..')
    axes[0].axhline(cfg['target'], color='black', linestyle=':', label='Target0.85')
    axes[0].set(xticks=x, xticklabels=['A cost2', 'B cost3', 'C cost4'], ylabel='Availability probability / session',
                title='Same authorized menu; axis zoom', ylim=(.78, .94))
    axes[0].legend(fontsize=8)
    axes[1].plot([r['width_fraction'] for r in sensitivity], [r['lower'] for r in sensitivity], label='B lower certificate')
    axes[1].axhline(cfg['target'], color='black', linestyle=':', label='Target0.85')
    axes[1].set(xlabel='Width fraction (1 = assumed input box)', ylabel='Lower availability probability / session',
                title='Nested-box sensitivity, deterministic')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Synthetic fixed-quorum3: parameter uncertainty is not confidence')
    fig.savefig(root/'results/interval_role.png', dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
