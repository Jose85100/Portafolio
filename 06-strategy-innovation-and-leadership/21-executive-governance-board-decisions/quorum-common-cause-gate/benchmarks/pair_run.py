"""Exact hypothetical joint-constraint audit; fair LP alternative with same inputs."""
from itertools import product
import json
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
from src.pair_assurance import pair_lower, required_pair_floor, choose_pair


def lp_pair(plan, risk, shock, floor):
    states = np.array(list(product((0, 1), repeat=3)))
    a = states.T
    pair = states[:, 1]*states[:, 2]
    marginals = (risk, plan.q1, plan.q2)
    s = shock.upper
    objective = (1-s)*states[:, 0] + s*np.all(states == 1, axis=1)
    result = linprog(objective, A_ub=np.vstack((a, -a, -pair)),
                     b_ub=[x.upper for x in marginals]+[-x.lower for x in marginals]+[-floor],
                     A_eq=np.ones((1, 8)), b_eq=[1], bounds=(0, None), method='highs')
    if not result.success:
        raise ValueError('LP constraint set infeasible: '+result.message)
    return result.fun, result.x, states


def load_pair_config():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root/'config_pair_assurance.json').read_text())
    base = json.loads((root/cfg['base_configuration']).read_text())
    plans = [IntervalPlan(x['name'], PI(*x['q1']), PI(*x['q2']), x['cost']) for x in base['plans']]
    return cfg, plans, PI(*base['risk']), PI(*base['shock'])


def main():
    root = Path(__file__).resolve().parents[1]
    cfg, plans, risk, shock = load_pair_config()
    floors, target = cfg['floors'], cfg['target']
    rows, witnesses = [], []
    for p in plans:
        lower = pair_lower(p, risk, shock, floors[p.name])
        lp, mass, states = lp_pair(p, risk, shock, floors[p.name])
        try:
            threshold = required_pair_floor(p, risk, shock, target)
        except ValueError:
            threshold = None
        rows.append({'plan': p.name, 'cost': p.cost, 'box_lower01nov': interval_bounds(p, risk, shock)['lower'],
                     'supplied_floor': floors[p.name], 'new_lower': lower, 'lp_lower': lp,
                     'required_floor': threshold, 'feasible_target': lower >= target-1e-12})
        for state, probability in zip(states, mass):
            witnesses.append({'plan': p.name, 'R': state[0], 'B1': state[1], 'B2': state[2], 'mass': probability})
    save(root/'results/pair_plans.csv', rows)
    save(root/'results/pair_witnesses.csv', witnesses)
    grid = []
    intervals = [PI(0, 0), PI(.2, .8), PI(1, 1)]
    for risk_i, q1, q2, shock_i in product(intervals, repeat=4):
        p = IntervalPlan('p', q1, q2, 0)
        cap = min(q1.upper, q2.upper)
        for floor in sorted({0., cap/2, cap}):
            lower = pair_lower(p, risk_i, shock_i, floor)
            lp, _, _ = lp_pair(p, risk_i, shock_i, floor)
            grid.append({'r_lo': risk_i.lower, 'r_hi': risk_i.upper, 'q1_lo': q1.lower, 'q1_hi': q1.upper,
                         'q2_lo': q2.lower, 'q2_hi': q2.upper, 's_lo': shock_i.lower, 's_hi': shock_i.upper,
                         'floor': floor, 'closed': lower, 'lp': lp, 'error': abs(lower-lp)})
    save(root/'results/pair_oracle.csv', grid)
    sensitivity = []
    # Choose the configured option with the largest strictly positive supplied floor.
    focus = max(plans, key=lambda p: floors[p.name])
    cap = min(focus.q1.upper, focus.q2.upper)
    for floor in np.linspace(0, cap, 101):
        sensitivity.append({'floor': floor, 'lower': pair_lower(focus, risk, shock, float(floor)),
                            'box_lower': interval_bounds(focus, risk, shock)['lower']})
    save(root/'results/pair_sensitivity.csv', sensitivity)
    lp_pair(focus, risk, shock, floors[focus.name])
    performance = []
    for n in (1, 10, 100):
        for method in ('closed_lower', 'lp8_lower'):
            for rep in range(5):
                tracemalloc.start()
                tick = time.perf_counter()
                for _ in range(n):
                    if method == 'closed_lower':
                        pair_lower(focus, risk, shock, floors[focus.name])
                    else:
                        lp_pair(focus, risk, shock, floors[focus.name])
                elapsed = time.perf_counter()-tick
                peak = tracemalloc.get_traced_memory()[1]
                tracemalloc.stop()
                performance.append({'n': n, 'method': method, 'repeat': rep, 'seconds': elapsed,
                                    'python_peak_bytes': peak})
    save(root/'results/pair_performance.csv', performance)
    def select_or_infeasible(method):
        try:
            return method().name
        except ValueError:
            return 'infeasible'
    common_floor = min(max(floors.values()), min(min(p.q1.upper, p.q2.upper) for p in plans))
    scenarios = [
        ('none', {p.name: 0.0 for p in plans}, target),
        ('configured_hypothetical', floors, target),
        ('same_floor_all_plans', {p.name: common_floor for p in plans}, target),
        ('redundant_focus_floor', {p.name: max(0., p.q1.lower+p.q2.lower-1)/2 if p.name == focus.name else 0. for p in plans}, target),
        ('higher_target', floors, .97),
    ]
    decisions = [{'scenario': label, 'target': t,
                  'selected': select_or_infeasible(lambda fs=fs, t=t: choose_pair(plans, risk, shock, fs, t))}
                 for label, fs, t in scenarios]
    save(root/'results/pair_decisions.csv', decisions)
    summary = {'target': target, 'plans': rows, 'focus_plan': focus.name, 'decision_ablations': decisions,
               'selected_box': select_or_infeasible(lambda: select_interval(plans, risk, shock, target)),
               'selected_supplied_constraints': select_or_infeasible(lambda: choose_pair(plans, risk, shock, floors, target)),
               'oracle_cases': len(grid), 'max_error': max(x['error'] for x in grid),
               'timing_n100_median_seconds': {m: median(x['seconds'] for x in performance if x['method'] == m and x['n'] == 100)
                                           for m in ('closed_lower', 'lp8_lower')},
               'python': platform.python_version(), 'platform': platform.platform(), 'processor': platform.processor(),
               'numpy': np.__version__, 'scipy': scipy.__version__, 'seed': None,
               'memory_scope': 'tracemalloc Python allocations; not native HiGHS or RSS',
               'source': cfg['data'], 'evidence_status': cfg['evidence_status']}
    (root/'results/pair_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    x = np.arange(len(plans))
    axes[0].bar(x-.15, [r['box_lower01nov'] for r in rows], .3, label='Box01nov', hatch='//')
    axes[0].bar(x+.15, [r['new_lower'] for r in rows], .3, label='Supplied pair constraint', hatch='..')
    axes[0].axhline(target, color='black', linestyle=':', label=f'Target{target:g}')
    axes[0].set(xticks=x, xticklabels=[f'{p.name} cost{p.cost:g}' for p in plans], ylim=(.78, .94),
                ylabel='Lower availability probability / session', title='Same menu and box; vertical axis zoom')
    axes[0].legend(fontsize=8)
    axes[1].plot([r['floor'] for r in sensitivity], [r['lower'] for r in sensitivity], label=f'{focus.name} lower certificate')
    axes[1].axhline(target, color='black', linestyle=':', label=f'Target{target:g}')
    axes[1].set(xlabel='Supplied pair co-attendance floor during shock',
                ylabel='Lower availability probability / session', title='Constraint strength, not observed evidence')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Synthetic committee: evidence requirement is not evidence obtained')
    fig.savefig(root/'results/pair_assurance.png', dpi=150)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
