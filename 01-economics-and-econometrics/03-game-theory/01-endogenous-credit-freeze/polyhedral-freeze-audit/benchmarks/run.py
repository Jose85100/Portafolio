"""Run exact cell audit, SciPy/HiGHS LP cross-checks, sampling and costs."""
import csv
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc

import numpy as np
from scipy.optimize import linprog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.polyhedra import (Game, equilibrium_cells, exact_regret,
                          player_region, serialize_cell)
sys.path.insert(0, str(ROOT.parent/'mixed-equilibrium-audit/src'))
from mixed import DegenerateGameError, solve as old_solve, mixed_regret, outcomes

SCENARIOS = {
    'regular': Game(),
    'coordination_family': Game(accuracy=.5),
    'full_indifference': Game(accuracy=.5, cost=.5, complementarity=0),
    'singular_but_isolated': Game(accuracy=1., cost=1.),
}


def write_csv(name, rows):
    with (ROOT/'results'/name).open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    rng = np.random.default_rng(20261015)
    summary = []; raw = {}; samples = []
    for label, game in SCENARIOS.items():
        cells = equilibrium_cells(game)
        try:
            count = len(old_solve(game)); old_status = 'isolated_list'
        except DegenerateGameError:
            count = -1; old_status = 'degenerate_rejected'
        summary.append(dict(scenario=label, maximal_cells=len(cells),
            dimensions=';'.join(str(c.dimension) for c in cells),
            max_dimension=max(c.dimension for c in cells),
            total_cell_vertices=sum(len(c.vertices) for c in cells),
            old_status=old_status, old_isolated_count=count))
        raw[label] = [serialize_cell(c) for c in cells]
        for index, cell in enumerate(cells):
            for draw in range(20):
                # Independent rational convex combinations in the two factors.
                left = [int(v) for v in rng.integers(1, 11, len(cell.left.vertices))]
                right = [int(v) for v in rng.integers(1, 11, len(cell.right.vertices))]
                p0 = tuple(sum(F(w)*v[k] for w, v in zip(left, cell.left.vertices))/sum(left) for k in (0, 1))
                p1 = tuple(sum(F(w)*v[k] for w, v in zip(right, cell.right.vertices))/sum(right) for k in (0, 1))
                point = p0+p1
                regret = exact_regret(game, point)
                assert regret == 0
                values = np.array([float(v) for v in point])
                samples.append(dict(scenario=label, cell=index, draw=draw,
                    point=';'.join(str(v) for v in point), exact_regret=str(regret),
                    float_regret=mixed_regret(game, values), **outcomes(game, values)))
    write_csv('summary.csv', summary)
    write_csv('samples.csv', samples)
    (ROOT/'results/cells.json').write_text(json.dumps(raw, indent=2))
    # Different algorithm: HiGHS LP support values and emptiness vs exact vertices.
    patterns = list(product((0, 1, 2), repeat=2)); oracle = []
    games = list(SCENARIOS.values())
    for case in range(60):
        game = games[int(rng.integers(0, len(games)))]
        own = patterns[int(rng.integers(0, 9))]; other = patterns[int(rng.integers(0, 9))]
        poly = player_region(game, own, other)
        for d in ((1., 0.), (0., 1.), (1., 1.), (-1., 2.)):
            res = linprog(-np.array(d),
                A_ub=np.array([[float(r[0]), float(r[1])] for r in poly.inequalities]),
                b_ub=np.array([float(r[2]) for r in poly.inequalities]),
                A_eq=np.array([[float(r[0]), float(r[1])] for r in poly.equalities]) if poly.equalities else None,
                b_eq=np.array([float(r[2]) for r in poly.equalities]) if poly.equalities else None,
                bounds=[(None, None), (None, None)], method='highs')
            if res.status == 2:
                assert not poly.vertices
                error = 0.; status = 'both_empty'
            else:
                assert res.success and poly.vertices
                exact_max = max(F(str(d[0]))*v[0]+F(str(d[1]))*v[1] for v in poly.vertices)
                error = abs(float(exact_max)+res.fun)
                assert error < 1e-9
                status = 'both_feasible'
            oracle.append(dict(case=case, own=str(own), other=str(other), direction=str(d),
                               status=status, error=error, exact_dimension=poly.dimension))
    write_csv('lp_oracle.csv', oracle)
    timings = []
    for count in (1, 5, 20):
        for method, solver in [('polyhedral_exact', equilibrium_cells), ('isolated_float', old_solve)]:
            for repeat in range(3):
                tracemalloc.start(); start = time.perf_counter()
                for _ in range(count): solver(Game())
                seconds = time.perf_counter()-start
                _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
                timings.append(dict(games=count, method=method, repeat=repeat,
                                    seconds=seconds, peak_python_bytes=peak))
    write_csv('timing.csv', timings)
    fig, ax = plt.subplots(figsize=(7, 5))
    family = equilibrium_cells(SCENARIOS['coordination_family'])[-1]
    grid = np.linspace(0, 1, 101)
    ax.plot(grid, 1-grid, color='#244e79', label='Each player: x(0)+x(1)=1')
    vertices = family.left.vertices
    ax.scatter([float(v[0]) for v in vertices], [float(v[1]) for v in vertices], color='#de9225', zorder=3)
    ax.set(xlabel='P(renew | signal=0)', ylabel='P(renew | signal=1)',
           title='Exact family: segment × segment, affine dimension 2', xlim=(-.05, 1.05), ylim=(-.05, 1.05))
    ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'results/family.png', dpi=150); plt.close(fig)
    cpu = next((r.split(':', 1)[1].strip() for r in Path('/proc/cpuinfo').read_text().splitlines()
                if r.startswith('model name')), 'unknown') if Path('/proc/cpuinfo').exists() else 'unknown'
    metadata = dict(date='2026-10-15', seed=20261015, support_patterns=81,
        base_commit='afcbc7facb17485786c02e539759afc31b5d23fd', python=sys.version,
        platform=platform.platform(), cpu=cpu,
        max_lp_error=max(r['error'] for r in oracle), max_float_regret=max(r['float_regret'] for r in samples),
        lp_checks=len(oracle), samples=len(samples),
        scenario_config={name:vars(g) for name, g in SCENARIOS.items()},
        memory='tracemalloc solver allocations; excludes native/RSS/input objects',
        hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'results').glob('*.csv')})
    (ROOT/'results/metadata.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
