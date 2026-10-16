"""External Nashpy cross-check; no completeness claim for degenerate games."""
import csv
import hashlib
import json
import platform
from pathlib import Path
import sys
import time
import tracemalloc
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nashpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from strategic import Game, matrices, nfg, parse_nfg, project, lift, strategic_regret
sys.path.insert(0, str(ROOT.parent/'polyhedral-freeze-audit/src'))
from polyhedra import equilibrium_cells
sys.path.insert(0, str(ROOT.parent/'mixed-equilibrium-audit/src'))
from mixed import mixed_regret


def write(name, rows):
    with (ROOT/'results'/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def external(g, method):
    a, b = parse_nfg(nfg(g))  # exercise exact interchange before external solver
    game = nashpy.Game(np.asarray(a, float), np.asarray(b, float))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            eq = list(getattr(game, method)())
            status = 'ok'
        except Exception as exc:  # record solver failures; never reinterpret as no equilibrium
            eq, status = [], type(exc).__name__+': '+str(exc)
    return eq, status, [str(w.message) for w in caught]


def main():
    results = ROOT/'results'
    results.mkdir(exist_ok=True)
    scenarios = dict(regular=Game(), coordination_family=Game(accuracy=.5),
                     full_indifference=Game(accuracy=.5, cost=.5, complementarity=0),
                     singular_isolated=Game(accuracy=1, cost=1))
    rng = np.random.default_rng(20261016)
    for k in range(8):
        scenarios[f'random_{k}'] = Game(prior=float(rng.uniform(.2, .8)),
            accuracy=float(rng.uniform(.55, .95)), cost=float(rng.uniform(.3, 1.2)))
    summary, raw, diagnostics, timing, stability = [], [], [], [], []
    for name, g in scenarios.items():
        (results/(name+'.nfg')).write_text(nfg(g))
        cells = equilibrium_cells(g)
        targets = sorted(set(v for c in cells for v in c.vertices))
        for method in ('vertex_enumeration', 'support_enumeration'):
            tracemalloc.start()
            start = time.perf_counter()
            equilibria, status, warning_messages = external(g, method)
            elapsed = time.perf_counter()-start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            projected = []
            worst = 0.
            for k, (p, r) in enumerate(equilibria):
                x = np.r_[project(p), project(r)]
                # Floating simplex roundoff is clipped only within 1e-10 accepted by project.
                x = np.clip(x, 0, 1)
                regret = mixed_regret(g, x)
                worst = max(worst, regret)
                if not any(np.max(abs(x-y)) <= 1e-8 for y in projected):
                    projected.append(x)
                raw.append(dict(scenario=name, method=method, index=k,
                                strategic_p=json.dumps(p.tolist()), strategic_r=json.dumps(r.tolist()),
                                behavioral=json.dumps(x.tolist()), interim_regret=regret))
            matched = sum(any(np.max(abs(np.array(v, float)-x)) <= 1e-8 for x in projected) for v in targets)
            distances = [min(np.max(abs(np.array(v, float)-x)) for x in projected) for v in targets] if projected else []
            for tolerance in (1e-12, 1e-10, 1e-8, 1e-6):
                stability.append(dict(scenario=name, method=method, tolerance=tolerance,
                                      matched_vertices=sum(d <= tolerance for d in distances), status=status))
            summary.append(dict(scenario=name, method=method, cells=len(cells),
                max_dimension=max(c.dimension for c in cells), target_vertices=len(targets),
                strategic_count=len(equilibria), behavioral_count=len(projected),
                matched_vertices=matched, max_interim_regret=worst if projected else '', status=status,
                max_min_vertex_error=max(distances) if distances else '',
                seconds=elapsed, peak_python_bytes=peak))
            diagnostics.append(dict(scenario=name, method=method, warnings=warning_messages, status=status))
            if name == 'regular' and method == 'vertex_enumeration':
                assert matched == 5 and worst < 1e-8, 'Primary prespecified hypothesis failed'
        for repeats in (1, 2, 4):
            for method in ('polyhedral', 'vertex_enumeration'):
                tracemalloc.start()
                start = time.perf_counter()
                status = 'ok'
                for _ in range(repeats):
                    if method == 'polyhedral':
                        equilibrium_cells(g)
                    else:
                        _, status, _ = external(g, method)
                elapsed = time.perf_counter()-start
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                timing.append(dict(scenario=name, method=method, batch_size=repeats,
                                   seconds=elapsed, peak_python_bytes=peak, status=status))
    # Negative ablation: ex-ante epsilon does NOT uniformly certify interim epsilon.
    negative = []
    for pi in (1e-2, 1e-4, 1e-8):
        g = Game(prior=pi, accuracy=1., cost=.5, complementarity=0.)
        a, b = matrices(g)
        p = lift(np.zeros(2))
        negative.append(dict(prior=pi, strategic_regret=strategic_regret(a, b, p, p),
                             interim_regret=mixed_regret(g, np.zeros(4))))
    write('summary.csv', summary)
    write('equilibria.csv', raw)
    write('timing.csv', timing)
    write('rare_type_ablation.csv', negative)
    write('stability.csv', stability)
    (results/'diagnostics.json').write_text(json.dumps(diagnostics, indent=2))
    (results/'config.json').write_text(json.dumps({name: vars(g) for name, g in scenarios.items()}, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    labels = list(scenarios)[:4]
    for method, offset, color, hatch in [('vertex_enumeration', -.18, '#1f77b4', ''),
                                          ('support_enumeration', .18, '#ff7f0e', '//')]:
        rows = [r for r in summary if r['scenario'] in labels and r['method'] == method]
        axes[0].bar(np.arange(4)+offset, [r['matched_vertices'] for r in rows], .35,
                    label=method.replace('_enumeration', ''), color=color, hatch=hatch, edgecolor='#333333', linewidth=.5)
    axes[0].set(xticks=range(4), xticklabels=['Regular', 'Family', 'Indifferent', 'Singular'],
                ylabel='Exact behavioral vertices matched (1e-8)', title='External solver cross-check')
    axes[0].legend()
    axes[0].annotate('solver error', (2-.18, 0), xytext=(1.3, 5),
                     arrowprops=dict(arrowstyle='->'), fontsize=9)
    axes[1].loglog([r['prior'] for r in negative], [r['strategic_regret'] for r in negative], 'o-', color='#1f77b4', label='Ex-ante regret')
    axes[1].loglog([r['prior'] for r in negative], [r['interim_regret'] for r in negative], 's--', color='#ff7f0e', label='Interim regret')
    axes[1].set(xlabel='Prior probability of good state (q=1)', ylabel='Payoff units', title='Negative control: rare-type masking')
    axes[1].legend()
    fig.savefig(results/'comparison.png', dpi=150)
    metadata = dict(seed=20261016, python=platform.python_version(), machine=platform.machine(),
                    platform=platform.platform(), cpu=platform.processor(), nashpy=nashpy.__version__,
                    numpy=np.__version__, source_commit='681836e',
                    memory='tracemalloc peak Python allocations, excludes native RSS',
                    threshold=1e-8, hashes={f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                    for f in results.glob('*.csv')})
    (results/'metadata.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(summary[:8], indent=2))


if __name__ == '__main__':
    main()
