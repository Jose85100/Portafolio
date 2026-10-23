"""Reproduce synthetic decision experiment, sensitivity and simulation oracle."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import platform
import resource
import time
import tracemalloc
import numpy as np
import scipy
from scipy.stats import beta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.evsi import Case, choose, evaluate


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / 'config.json').read_text())
    case = Case(**{k: cfg[k] for k in Case.__dataclass_fields__})
    tracemalloc.start()
    start = time.perf_counter()
    rows = [evaluate(case, n) for n in cfg['sizes']]
    duration = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    selected = choose(case, cfg['sizes'])
    rng = np.random.default_rng(cfg['seed'])
    p = rng.beta(case.alpha, case.beta, cfg['mc_replicates'])
    n = int(selected['n'])
    k = rng.binomial(n, p)
    action = case.payoff((case.alpha + k) / (case.alpha + case.beta + n)) > 0
    realized = action * case.payoff(p) - selected['experiment_cost']
    mc_mean = float(np.mean(realized))
    mc_se = float(np.std(realized, ddof=1) / np.sqrt(len(realized)))
    threshold = (case.unit_cost + case.fixed_rollout / case.population) / case.benefit
    perfect = case.population * case.benefit * case.alpha / (case.alpha + case.beta) * beta.sf(threshold, case.alpha + 1, case.beta) - (case.population * case.unit_cost + case.fixed_rollout) * beta.sf(threshold, case.alpha, case.beta)
    evpi = float(perfect - rows[0]['immediate_value'])
    assert abs(mc_mean - selected['net_value']) < 5 * mc_se
    assert 0 <= selected['evsi'] <= evpi + 1e-8
    assert selected['increment'] >= cfg['hypothesis_min_increment']
    scaling = []
    for candidate in (100, 1000, 10000):
        times = []
        for _ in range(5):
            start_n = time.perf_counter()
            evaluate(case, candidate)
            times.append(time.perf_counter() - start_n)
        scaling.append({'n': candidate, 'repetitions': 5, 'median_seconds': float(np.median(times)),
                        'min_seconds': min(times), 'max_seconds': max(times)})
    with (root / 'results' / 'scaling.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(scaling[0]))
        writer.writeheader()
        writer.writerows(scaling)
    sensitivity = []
    for strength in (1, 5, 20):
        for cost in (0.0, 5.0, 25.0, 100.0):
            c = replace(case, alpha=case.alpha * strength, beta=case.beta * strength, experiment_unit=cost)
            sensitivity.append({'prior_multiplier': strength, 'study_unit_cost': cost, **choose(c, cfg['sizes'])})
    for name, data in [('designs', rows), ('sensitivity', sensitivity)]:
        with (root / 'results' / f'{name}.csv').open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    # Raw simulated evidence is aggregate per 1,000 draws, not cherry-picked.
    with (root / 'results' / 'mc_batches.csv').open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['batch', 'draws', 'mean_net_value', 'rollout_rate'])
        for i in range(0, len(p), 1000):
            writer.writerow([i // 1000, 1000, realized[i:i+1000].mean(), action[i:i+1000].mean()])
    summary = {'selected': selected, 'baseline_immediate': rows[0],
               'baseline_fixed_n100': evaluate(case, 100), 'evpi': evpi,
               'mc_mean': mc_mean, 'mc_standard_error': mc_se,
               'design_runtime_seconds': duration, 'python_peak_bytes': peak,
               'process_peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'seed': cfg['seed'], 'replicates': len(p), 'python': platform.python_version(),
               'platform': platform.platform(), 'processor': platform.processor() or 'not exposed',
               'numpy': np.__version__, 'scipy': scipy.__version__, 'matplotlib': matplotlib.__version__}
    (root / 'results' / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot([r['n'] for r in rows], [r['net_value'] for r in rows], 'o-', color='#176B87', label='Estudiar y decidir después')
    ax.axhline(rows[0]['net_value'], color='#A23B3B', linestyle='--', label='Decidir hoy')
    ax.scatter([selected['n']], [selected['net_value']], color='#E09F3E', s=100, zorder=3, label='Mejor candidato')
    ax.set(xlabel='Tamaño del piloto (observaciones)', ylabel='Valor esperado neto (unidades sintéticas)', title='Un piloto mayor no siempre crea más valor neto')
    ax.legend()
    fig.tight_layout()
    fig.savefig(root / 'results' / 'decision_curve.png', dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
