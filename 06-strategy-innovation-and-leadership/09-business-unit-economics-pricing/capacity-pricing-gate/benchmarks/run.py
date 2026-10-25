"""Finite scenario pricing audit; no estimated or observed demand claims."""
import csv
import json
from pathlib import Path
import platform
import time
import tracemalloc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.pricing import Scenario, choose, evaluate, profit


def write_csv(path, rows):
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root/'config.json').read_text())
    scenarios = [Scenario(**s) for s in cfg['scenarios']]
    args = (cfg['capacity'], cfg['unit_cost'], cfg['fixed_cost'], cfg['alpha'])
    tracemalloc.start()
    start = time.perf_counter()
    constrained = choose(cfg['prices'], scenarios, *args, cfg['budget'])
    elapsed = time.perf_counter()-start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    neutral = choose(cfg['prices'], scenarios, *args)
    mean_arrivals = sum(s.weight*s.arrivals for s in scenarios)
    plugin = choose(cfg['prices'], [Scenario('mean', 1, mean_arrivals)], *args)
    plugin_actual = evaluate(plugin['price'], scenarios, *args)
    rows = []
    for p in [None, *cfg['prices']]:
        row = evaluate(p, scenarios, *args)
        rows.append({'price': 'stop' if p is None else p,
                     'expected_profit': row['expected_profit'], 'cvar_shortfall': row['cvar_shortfall'],
                     **{s.name+'_profit': value for s, value in zip(scenarios, row['scenario_profits'])}})
    write_csv(root/'results'/'prices.csv', rows)
    scaling = []
    for count in (17, 161, 1601):
        menu = list(np.linspace(8, 40, count))
        timings = []
        for _ in range(5):
            tick = time.perf_counter()
            choice = choose(menu, scenarios, *args, cfg['budget'])
            timings.append(time.perf_counter()-tick)
        scaling.append({'menu_size': count, 'median_seconds': float(np.median(timings)),
                        'selected_price': choice['price'], 'expected_profit': choice['expected_profit'],
                        'cvar_shortfall': choice['cvar_shortfall']})
    write_csv(root/'results'/'scaling.csv', scaling)
    sensitivity = []
    for capacity in (100, 300, 600):
        for budget in (0, 300, 500, 1000):
            result = choose(cfg['prices'], scenarios, capacity, cfg['unit_cost'], cfg['fixed_cost'], cfg['alpha'], budget)
            sensitivity.append({'capacity': capacity, 'budget': budget,
                                **{k:v for k,v in result.items() if k!='scenario_profits'}})
    write_csv(root/'results'/'sensitivity.csv', sensitivity)
    rng = np.random.default_rng(cfg['seed'])
    indices = rng.choice(len(scenarios), 200000, p=[s.weight for s in scenarios])
    p = constrained['price']
    payoffs = np.array([profit(p, s, *args[:3]) if p is not None else 0 for s in scenarios])
    samples = payoffs[indices]
    mc_mean, mc_se = float(np.mean(samples)), float(np.std(samples, ddof=1)/np.sqrt(len(samples)))
    assert abs(mc_mean-constrained['expected_profit']) < 5*mc_se+1e-8
    assert constrained['cvar_shortfall'] <= cfg['budget']+1e-8
    assert constrained['expected_profit'] <= neutral['expected_profit']+1e-8
    write_csv(root/'results'/'mc_scenarios.csv', [{'scenario': s.name, 'draws': int(np.sum(indices==i)), 'payoff': payoffs[i]} for i,s in enumerate(scenarios)])
    summary = {'constrained': constrained, 'risk_neutral': neutral, 'plugin_prediction': plugin,
               'plugin_actual': plugin_actual, 'mc_mean': mc_mean, 'mc_se': mc_se,
               'replicates': len(samples), 'selector_seconds': elapsed, 'selector_python_peak_bytes': peak,
               'seed': cfg['seed'], 'python': platform.python_version(), 'platform': platform.platform(), 'numpy': np.__version__}
    (root/'results'/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(1,2,figsize=(10,4.5))
    prices = [r['price'] for r in rows[1:]]
    axes[0].plot(prices, [r['expected_profit'] for r in rows[1:]], 'o-', color='#176B87')
    axes[0].axvline(constrained['price'], linestyle='--', color='#E09F3E', label='Precio con presupuesto')
    axes[0].set(xlabel='Precio sintético / transacción', ylabel='Beneficio esperado / período', title='Valor esperado y restricción')
    axes[0].legend()
    axes[1].plot(prices, [r['cvar_shortfall'] for r in rows[1:]], 's-', color='#A23B3B')
    axes[1].axhline(cfg['budget'], linestyle='--', color='black', label='Presupuesto: 500')
    axes[1].set(xlabel='Precio sintético / transacción', ylabel='CVaR 90% de max(−beneficio, 0)', title='Peor 10% de masa; átomos fraccionados')
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(root/'results'/'pricing-frontier.png', dpi=150)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
