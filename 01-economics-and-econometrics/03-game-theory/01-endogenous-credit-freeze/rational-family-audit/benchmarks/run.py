"""Exact external-family comparison, with raw profiles, timing and falsification."""
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import random
import sys
import time
import tracemalloc
from importlib.metadata import version
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from families import Game, audit, matrices, nfg, regret, dimension
sys.path.insert(0, str(ROOT.parent/'polyhedral-freeze-audit/src'))
from polyhedra import equilibrium_cells, exact_regret


def save(name, rows):
    with (ROOT/'results'/name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def measured(fn):
    tracemalloc.start()
    start = time.perf_counter()
    output = fn()
    elapsed = time.perf_counter()-start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return output, elapsed, peak


def baseline(g):
    return sorted((c.left.vertices, c.right.vertices) for c in equilibrium_cells(g))


def mixture(poly, rng):
    weights = [rng.randrange(1, 10) for _ in poly]
    return tuple(sum(F(w, sum(weights))*v[k] for w, v in zip(weights, poly)) for k in (0, 1))


def main():
    results = ROOT/'results'
    results.mkdir(exist_ok=True)
    rng = random.Random(20261017)
    scenarios = dict(regular=Game(), coordination_family=Game(accuracy=.5),
        full_indifference=Game(accuracy=.5, cost=.5, complementarity=0),
        singular_isolated=Game(accuracy=1, cost=1), near_family=Game(accuracy=.500000001))
    for k in range(8):
        scenarios[f'random_{k}'] = Game(prior=rng.randint(2, 8)/10,
            accuracy=rng.randint(5, 10)/10, cost=rng.randint(1, 12)/10)
    summary, timing, raw, samples, family_dump = [], [], [], [], {}
    for name, g in scenarios.items():
        (results/(name+'.nfg')).write_text(nfg(g))
        (profiles, cells), ext_seconds, ext_peak = measured(lambda: audit(g))
        expected, base_seconds, base_peak = measured(lambda: baseline(g))
        identical = cells == expected
        assert identical, f'Exact family mismatch: {name}'
        dimensions = [dimension(a)+dimension(b) for a, b in cells]
        family_dump[name] = [[[list(map(str, p)) for p in poly] for poly in family] for family in cells]
        for k, (p, q) in enumerate(profiles):
            raw.append(dict(scenario=name, profile=k, player0=json.dumps(list(map(str, p))),
                            player1=json.dumps(list(map(str, q)))))
        worst = F(0)
        for k, (left, right) in enumerate(cells):
            for draw in range(10):
                x, y = mixture(left, rng), mixture(right, rng)
                value = exact_regret(g, x+y)
                worst = max(worst, value)
                samples.append(dict(scenario=name, family=k, draw=draw,
                    probabilities=json.dumps(list(map(str, x+y))), exact_interim_regret=str(value)))
        assert worst == 0, f'Interim regret failed: {name}'
        summary.append(dict(scenario=name, gambit_profiles=len(profiles),
            baseline_families=len(expected), reconstructed_families=len(cells),
            dimensions=json.dumps(dimensions), exact_equal=identical, max_interim_regret=str(worst),
            external_seconds=ext_seconds, baseline_seconds=base_seconds,
            external_peak_python_bytes=ext_peak, baseline_peak_python_bytes=base_peak))
        for repeats in (1, 2, 4):
            for method, fn in [('gambit_reconstruct', lambda: audit(g)), ('polyhedral', lambda: baseline(g))]:
                _, seconds, peak = measured(lambda: [fn() for _ in range(repeats)])
                timing.append(dict(scenario=name, method=method, batch_size=repeats,
                                   seconds=seconds, peak_python_bytes=peak))
    negative = []
    for name in ('regular', 'coordination_family', 'full_indifference'):
        g = scenarios[name]
        profiles, cells = audit(g)
        point = (F(1, 2), F(1, 2))
        negative.append(dict(scenario=name, ablation='convexify_all_equilibria',
            candidate='[1/2,1/2,1/2,1/2]', exact_exante_regret=str(regret(*matrices(g), point, point)),
            true_max_dimension=max(dimension(a)+dimension(b) for a, b in cells),
            first_profile_only_dimension=0, profiles=len(profiles)))
    save('summary.csv', summary)
    save('timing.csv', timing)
    save('profiles.csv', raw)
    save('samples.csv', samples)
    save('ablations.csv', negative)
    (results/'families.json').write_text(json.dumps(family_dump, indent=2))
    (results/'config.json').write_text(json.dumps({name: vars(g) for name, g in scenarios.items()}, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    selected = summary[:5]
    axes[0].bar(range(5), [r['baseline_families'] for r in selected], color='#e8e8e8', edgecolor='#333333', label='Exact baseline')
    axes[0].plot(range(5), [r['reconstructed_families'] for r in selected], 'o', color='#1f77b4', label='Gambit + reconstruction')
    axes[0].set(xticks=range(5), xticklabels=['Regular', 'Family', 'Indiff.', 'Singular', 'Near'],
                ylabel='Containment-maximal product families', title='Exact comparison: five canonical cases')
    axes[0].legend(fontsize=9)
    axes[1].bar(range(3), [float(F(r['exact_exante_regret'])) for r in negative], color='#ff7f0e', hatch='//')
    axes[1].set(xticks=range(3), xticklabels=['Regular', 'Family', 'Indifference'],
                ylabel='Ex-ante regret, midpoint (payoff units)', title='Negative control: convexify everything')
    fig.savefig(results/'comparison.png', dpi=150)
    metadata = dict(seed=20261017, python=platform.python_version(), platform=platform.platform(),
        cpu=platform.processor(), pygambit=version('pygambit'), source_base='b19c03599a1f7cbb88a17eaed65fdd590dbb009a',
        matching='exact rational equality, no numeric tolerance', measured_samples=len(samples),
        memory='tracemalloc Python allocation peak, excludes C++ Gambit and native RSS',
        hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in results.glob('*.csv')})
    (results/'metadata.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(summary[:5], indent=2))
    print('Exact sample regret zero:', len(samples))


if __name__ == '__main__':
    main()
