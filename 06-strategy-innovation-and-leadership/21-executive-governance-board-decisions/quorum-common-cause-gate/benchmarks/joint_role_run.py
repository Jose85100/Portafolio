"""Deterministic joint-role audit; LP is a competitive exact alternative."""
import csv
from itertools import product
import json
from pathlib import Path
import platform
from statistics import median
import time
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.optimize import linprog
from src.joint_role import joint_bounds, select_joint
from src.reserve_ambiguity import ReservePlan, choose_plan


def save(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def oracle(r, q1, q2, sign=1):
    states = np.array(list(product((0, 1), repeat=3)))
    objective = np.zeros(8)
    objective[-1] = sign
    result = linprog(objective, A_eq=np.vstack((np.ones(8), states.T)),
                     b_eq=[1, r, q1, q2], bounds=(0, None), method='highs')
    assert result.success, result.message
    return result, states


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root/'config_joint_role.json').read_text())
    plans = [ReservePlan(**p) for p in cfg['plans']]
    rows = [{'name': p.name, 'q1': p.q1, 'q2': p.q2, 'cost': p.cost,
             **joint_bounds(p, cfg['shock'], cfg['risk'])} for p in plans]
    save(root/'results/joint_role_plans.csv', rows)
    grid = []
    for r, q1, q2 in product((0, .2, .7, .95, 1), repeat=3):
        b = joint_bounds(ReservePlan('p', q1, q2, 0), shock=1, risk=r)
        lo, _ = oracle(r, q1, q2)
        hi, _ = oracle(r, q1, q2, -1)
        grid.append({'r': r, 'q1': q1, 'q2': q2, 'lower': b['lower'],
                     'upper': b['upper'], 'lp_lower': lo.fun, 'lp_upper': -hi.fun,
                     'max_error': max(abs(b['lower']-lo.fun), abs(b['upper']+hi.fun))})
    save(root/'results/joint_role_oracle.csv', grid)
    witnesses = []
    for p in plans:
        lp, states = oracle(cfg['risk'], p.q1, p.q2)
        for state, mass in zip(states, lp.x):
            witnesses.append({'plan': p.name, 'R': state[0], 'B1': state[1],
                              'B2': state[2], 'mass': mass, 'event': int(all(state))})
    save(root/'results/joint_role_witnesses.csv', witnesses)
    sensitivity = []
    for i in range(101):
        r = i/100
        b = joint_bounds(plans[1], cfg['shock'], r)
        sensitivity.append({'r': r, **b})
    save(root/'results/joint_role_sensitivity.csv', sensitivity)
    targets = [.85, .872, .90, .97]
    decisions = []
    for t in targets:
        for method in ('nominal', 'restricted30', 'joint31'):
            try:
                if method == 'joint31':
                    selected = select_joint(plans, t, cfg['shock'], cfg['risk']).name
                else:
                    selected = choose_plan(plans, t, cfg['shock'], cfg['risk'],
                                           robust=method == 'restricted30')['name']
            except ValueError:
                selected = 'infeasible'
            decisions.append({'target': t, 'method': method, 'selected': selected})
    save(root/'results/joint_role_decisions.csv', decisions)
    # Warm both alternatives before measuring steady computation, excluding imports.
    oracle(.95, .8, .8)
    perf = []
    for n in (1, 10, 100):
        for method in ('closed', 'lp8'):
            for rep in range(5):
                tracemalloc.start()
                tick = time.perf_counter()
                for _ in range(n):
                    if method == 'closed':
                        joint_bounds(plans[1], cfg['shock'], cfg['risk'])
                    else:
                        oracle(cfg['risk'], .8, .8)
                elapsed = time.perf_counter()-tick
                peak = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                perf.append({'n': n, 'method': method, 'repeat': rep,
                             'compute_seconds': elapsed, 'python_peak_bytes': peak})
    save(root/'results/joint_role_performance.csv', perf)
    summary = {'oracle_cases': len(grid), 'lp_objectives': 2*len(grid),
               'max_error': max(x['max_error'] for x in grid),
               'plans': rows, 'decisions': decisions,
               'timings_n100_median_seconds': {m: median(x['compute_seconds'] for x in perf
                  if x['method'] == m and x['n'] == 100) for m in ('closed', 'lp8')},
               'python': platform.python_version(), 'platform': platform.platform(),
               'processor': platform.processor(), 'numpy': np.__version__, 'scipy': scipy.__version__,
               'memory_scope': 'tracemalloc Python allocations; not native HiGHS/RSS',
               'data': cfg['data'], 'seed': None}
    (root/'results/joint_role_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    x = np.arange(3)
    for delta, key, label in ((-.22, 'nominal', 'Independent nominal'),
                              (0, 'restricted_lower30', 'Role independent (30)'),
                              (.22, 'lower', 'Joint lower (31)')):
        axes[0].bar(x+delta, [r[key] for r in rows], .22, label=label)
    axes[0].axhline(.872, color='black', linestyle=':', label='Designed target 0.872')
    axes[0].set(xticks=x, xticklabels=['A: cost2', 'B: cost3', 'C: cost4'],
                ylabel='Availability probability / session', ylim=(.8, .94),
                title='Same marginals and authorized menu')
    axes[0].legend(fontsize=8)
    for key, label, style in (('restricted_lower30', 'Role independent (30)', '--'),
                              ('lower', 'Arbitrary joint (31)', '-')):
        axes[1].plot([r['r'] for r in sensitivity], [r[key] for r in sensitivity],
                     style, label=label)
    axes[1].set(xlabel='Mandatory-role marginal attendance r',
                ylabel='Lower availability probability / session', title='Plan B: q1=q2=0.8, shock weight0.2')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Synthetic fixed-quorum3 committee: dependency audit')
    fig.savefig(root/'results/joint_role.png', dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
