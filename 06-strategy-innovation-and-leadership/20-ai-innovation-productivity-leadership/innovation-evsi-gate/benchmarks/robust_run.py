"""Prior/delay sensitivity; common policies are evaluated across same scenarios."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.evsi import Case
from src.robust import select


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / 'robust-config.json').read_text())
    c = Case(**cfg['case'])
    priors = tuple(tuple(p) for p in cfg['priors'])
    start = time.perf_counter()
    rows = []
    for discount in cfg['discounts']:
        for robust in (False, True):
            result = select(c, cfg['sizes'], priors, discount,
                            cfg['observations_per_day'], robust)
            best = result['selected']
            rows.append({'daily_discount': discount, 'policy': 'robust' if robust else 'nominal',
                         'n': best['n'], 'worst_value': best['worst_value'],
                         'objective': best['objective'],
                         **{f'prior_{i}_value': value for i, value in enumerate(best['scenario_values'])}})
    with (root / 'results' / 'robust-designs.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    # Independent payoff simulation checks selected common robust rule.
    chosen = select(c, cfg['sizes'], priors, cfg['discounts'][0], cfg['observations_per_day'], True)['selected']
    n = chosen['n']
    rng = np.random.default_rng(cfg['seed'])
    checks = []
    for i, (a, b) in enumerate(priors):
        scenario = replace(c, alpha=a, beta=b)
        p = rng.beta(a, b, cfg['replicates'])
        k = rng.binomial(n, p)
        terminal = np.minimum.reduce([scenario.payoff((aa + k) / (aa + bb + n)) for aa, bb in priors]) > 0
        cost = c.experiment_fixed + n * c.experiment_unit if n else 0
        values = np.exp(-cfg['discounts'][0] * n / cfg['observations_per_day']) * terminal * scenario.payoff(p) - cost
        mean, se = float(np.mean(values)), float(np.std(values, ddof=1) / np.sqrt(len(values)))
        exact = chosen['scenario_values'][i]
        assert abs(mean - exact) <= 5 * se + 1e-8
        checks.append({'prior': [a, b], 'exact': exact, 'mc_mean': mean, 'mc_se': se})
    summary = {'selected_robust': chosen, 'mc_checks': checks,
               'runtime_seconds': time.perf_counter() - start,
               'seed': cfg['seed'], 'replicates_per_prior': cfg['replicates']}
    (root / 'results' / 'robust-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for policy, marker, color in [('nominal', 'o', '#A23B3B'), ('robust', 's', '#176B87')]:
        subset = [r for r in rows if r['policy'] == policy]
        ax.plot([r['daily_discount'] for r in subset], [r['worst_value'] for r in subset], marker=marker, color=color, label=policy)
    ax.axhline(0, color='black', linewidth=.8)
    ax.set(xlabel='Tasa diaria de descuento continuo', ylabel='Peor valor esperado (unidades sintéticas)', title='Robustez del piloto ante prior y demora')
    ax.legend()
    fig.tight_layout()
    fig.savefig(root/'results'/'robust-decision.png', dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
