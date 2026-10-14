"""Execute support audit, rational cross-check, negative cases and costs."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.mixed import (DegenerateGameError, Game, mixed_regret, outcomes,
                       pure_baseline, rational_oracle, solve)

ROOT = Path(__file__).resolve().parents[1]


def write_csv(name, rows):
    with (ROOT/'results'/name).open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    g = Game(); points = solve(g); pure = pure_baseline(g)
    rows = [dict(p00=float(p[0]), p01=float(p[1]), p10=float(p[2]), p11=float(p[3]),
                 is_pure=int(np.all((p == 0) | (p == 1))), regret=mixed_regret(g, p), **outcomes(g, p))
            for p in points]
    write_csv('equilibria.csv', rows)
    rng = np.random.default_rng(20261014); oracle_rows = []
    for case in range(50):
        params = dict(accuracy=int(rng.integers(61, 95))/100, cost=int(rng.integers(11, 150))/100,
                      complementarity=int(rng.integers(21, 140))/100)
        game = Game(**params)
        try:
            floating = solve(game)
        except DegenerateGameError:
            oracle_rows.append(dict(case=case, **params, status='degenerate', count=-1, mismatch=-1, error=-1.))
            continue
        exact = np.array(rational_oracle(game), dtype=float)
        error = max(min(float(np.max(np.abs(p-v))) for v in exact) for p in floating)
        mismatch = int(len(floating) != len(exact) or error > 1e-9)
        assert not mismatch
        oracle_rows.append(dict(case=case, **params, status='isolated', count=len(floating), mismatch=mismatch, error=error))
    write_csv('oracle.csv', oracle_rows)
    sensitivity = []
    for cost in np.linspace(.45, 1.15, 15):
        for alpha in np.linspace(.4, 1.2, 13):
            game = Game(cost=float(cost), complementarity=float(alpha))
            baseline = pure_baseline(game)
            try:
                all_points = solve(game)
                freezes = [outcomes(game, p)['freeze_given_good'] for p in all_points]
                sensitivity.append(dict(cost=cost, alpha=alpha, status='isolated',
                    pure_count=len(baseline), total_count=len(all_points),
                    freeze_min=min(freezes), freeze_max=max(freezes)))
            except DegenerateGameError:
                sensitivity.append(dict(cost=cost, alpha=alpha, status='degenerate',
                    pure_count=len(baseline), total_count=-1, freeze_min=-1., freeze_max=-1.))
    write_csv('sensitivity.csv', sensitivity)
    timing = []
    for count in (10, 50, 100):
        games = [Game(cost=.91+.001*(i % 17), complementarity=.81+.003*(i % 13)) for i in range(count)]
        for name, solver in [('pure_baseline', pure_baseline), ('mixed_support', solve)]:
            for repeat in range(3):
                tracemalloc.start(); start = time.perf_counter()
                for game in games: solver(game)
                seconds = time.perf_counter()-start
                _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
                timing.append(dict(games=count, method=name, repeat=repeat, seconds=seconds, peak_python_bytes=peak))
    write_csv('timing.csv', timing)
    stability = [dict(tolerance=tol, count=len(solve(g, tol)),
                      max_regret=max(mixed_regret(g, p) for p in solve(g, tol)))
                 for tol in (1e-12, 1e-10, 1e-8)]
    write_csv('stability.csv', stability)
    negative = []
    for label, game in [('zero_alpha', Game(complementarity=0)),
                        ('indifference', Game(accuracy=.5, cost=.5, complementarity=0))]:
        try:
            result = solve(game); status = 'isolated'; count = len(result)
        except DegenerateGameError:
            status = 'degenerate_rejected'; count = -1
        negative.append(dict(case=label, status=status, mixed_count=count, pure_count=len(pure_baseline(game))))
    write_csv('negative.csv', negative)
    pure_freezes = [outcomes(g, p)['freeze_given_good'] for p in pure]
    all_freezes = [r['freeze_given_good'] for r in rows]
    summary = dict(pure_count=len(pure), mixed_inclusive_count=len(points),
        new_mixed=len(points)-len(pure), pure_bounds=[min(pure_freezes), max(pure_freezes)],
        mixed_bounds=[min(all_freezes), max(all_freezes)],
        oracle_cases=len(oracle_rows), oracle_isolated=sum(r['status'] == 'isolated' for r in oracle_rows),
        oracle_mismatches=sum(r['mismatch'] == 1 for r in oracle_rows),
        max_oracle_error=max(r['error'] for r in oracle_rows),
        sensitivity_cases=len(sensitivity), rejected_degenerate=sum(r['status'] == 'degenerate' for r in sensitivity),
        max_regret=max(r['regret'] for r in rows))
    (ROOT/'results/summary.json').write_text(json.dumps(summary, indent=2))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(rows)), all_freezes, color=['#224c78' if r['is_pure'] else '#e39a32' for r in rows])
    ax.set_xticks(range(len(rows)), ['withdraw', 'mix high', 'signal', 'mix low', 'always'])
    ax.set(ylabel='P(no renewal | good fundamental)', title='Pure (blue) and additional mixed (orange) BNE', ylim=(0, 1.05))
    fig.tight_layout(); fig.savefig(ROOT/'results/comparison.png', dpi=150); plt.close(fig)
    cpu = next((s.split(':', 1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines()
                if s.startswith('model name')), 'unknown') if Path('/proc/cpuinfo').exists() else 'unknown'
    metadata = dict(date='2026-10-14', seed=20261014, prior=.5, accuracy=.8, cost=.9, alpha=.8,
        support_patterns=81, python=sys.version, numpy=np.__version__, cpu=cpu, platform=platform.platform(),
        memory='tracemalloc: solver allocations only, not RSS/native/input objects',
        hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'results').glob('*.csv')})
    (ROOT/'results/metadata.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
