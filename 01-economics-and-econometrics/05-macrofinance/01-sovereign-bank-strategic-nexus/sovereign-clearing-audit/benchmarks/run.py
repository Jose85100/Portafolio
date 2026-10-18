"""Sovereign stress, reference-notebook regression, oracles and near-closure ablation."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from clearing import Network, assets, bracket, residual_only, lp_clear, rational_clear, accounting, step


def ring(n=3, anchor=.1):
    debt = np.zeros((n, n))
    for i in range(n):
        debt[i, (i+1) % n] = 1-anchor
    return Network(debt, np.full(n, anchor))


def save(name, records):
    with (ROOT/'results'/name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)


def measured(fn):
    tracemalloc.start()
    start = time.perf_counter()
    result = fn()
    seconds = time.perf_counter()-start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, seconds, peak


def main():
    out = ROOT/'results'
    out.mkdir(exist_ok=True)
    rng = np.random.default_rng(20261018)
    net = ring()
    cash, sovereign = np.array([0., .1, .1]), np.array([.1, 0, 0])
    stress, bank_rows = [], []
    for h in np.linspace(0, 1, 11):
        x = assets(net, cash, sovereign, float(h))
        result = bracket(net, x)
        oracle = lp_clear(net, x)
        one_pass = step(net, x, net.total)
        a = accounting(net, x, result.payments)
        direct = accounting(net, x, one_pass)
        assert np.abs(result.payments-oracle).sum() < 1e-7
        assert abs(a['resource_identity_error']) < 1e-8
        stress.append(dict(haircut=h, direct_sovereign_loss=h*sovereign.sum(),
            one_pass_gross=direct['gross_unpaid'], clearing_gross=a['gross_unpaid'],
            clearing_outside=a['outside_unpaid'], one_pass_resource_error=direct['resource_identity_error'],
            resource_error=a['resource_identity_error'], iterations=result.iterations,
            width_l1=result.width_l1, lp_error_l1=float(np.abs(result.payments-oracle).sum())))
        for i, p in enumerate(result.payments):
            bank_rows.append(dict(haircut=h, bank=i, external_assets=x[i], obligations=net.total[i],
                                  payments=p, unpaid=net.total[i]-p))
    # Read and run the actual experiment definition from the existing weekly notebook.
    weekly_path = ROOT.parents[1]/'04-liquidity-contagion-network/notebooks/01-estimation-and-robustness.ipynb'
    notebook = json.loads(weekly_path.read_text())
    definitions = []
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            definitions.extend(node for node in ast.parse(''.join(cell['source'])).body
                               if isinstance(node, ast.FunctionDef) and node.name == 'experiment')
    assert len(definitions) == 1
    namespace = {'np': np}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(weekly_path), 'exec'), namespace)
    weekly = []
    pi = np.array([[0, .5, .2, 0], [.4, 0, .3, 0], [0, .3, 0, .4], [.3, 0, .3, 0]])
    weekly_net = Network(pi*10, (1-pi.sum(axis=1))*10)
    for h in (0., .25, .5, .75, 1.):
        original, _ = namespace['experiment'](rng, h)
        x = np.full(4, 4.)
        x[0] *= 1-h
        result = bracket(weekly_net, x, tolerance=1e-10)
        gross = accounting(weekly_net, x, result.payments)['gross_unpaid']
        discrepancy = abs(gross-original['Impago final'])
        assert discrepancy < 1e-8
        weekly.append(dict(haircut=h, notebook_gross=original['Impago final'], modular_gross=gross, difference=discrepancy))
    # Rational active-set oracle, independent of LP and iterative stopping.
    oracle_rows = []
    for k in range(30):
        debt = rng.integers(0, 10, (3, 3))/10
        np.fill_diagonal(debt, 0)
        case = Network(debt, np.full(3, .2))
        x = rng.integers(0, 10, 3)/10
        truth_q = rational_clear(case, x)
        truth = np.array(truth_q, float)
        result = bracket(case, x)
        lp = lp_clear(case, x)
        err = float(np.abs(result.payments-truth).sum())
        lp_error = float(np.abs(lp-truth).sum())
        assert err <= result.width_l1+1e-12 and lp_error < 1e-7
        oracle_rows.append(dict(case=k, liabilities=json.dumps(debt.tolist()), resources=json.dumps(x.tolist()),
            truth=json.dumps(list(map(str, truth_q))), bracket_error_l1=err, lp_error_l1=lp_error,
            width_l1=result.width_l1, iterations=result.iterations))
    near = []
    for anchor in (.1, .01, .001, 1e-9):
        case = ring(anchor=anchor)
        x = np.full(3, anchor/2)
        truth = np.array(rational_clear(case, x), float)
        for name, fn in [('residual_only', lambda: residual_only(case, x)),
                         ('two_sided', lambda: bracket(case, x))]:
            start = time.perf_counter()
            try:
                r = fn()
                row = dict(anchor=anchor, method=name, status='accepted', iterations=r.iterations,
                    residual_l1=r.residual_l1, error_l1=float(np.abs(r.payments-truth).sum()),
                    width_l1=r.width_l1 if np.isfinite(r.width_l1) else '')
            except RuntimeError as exc:
                row = dict(anchor=anchor, method=name, status=str(exc), iterations=10000,
                           residual_l1='', error_l1='', width_l1='')
            row['seconds'] = time.perf_counter()-start
            near.append(row)
        lp = lp_clear(case, x)
        near.append(dict(anchor=anchor, method='LP', status='solver_success_not_accuracy_certificate', iterations='',
            residual_l1=float(np.abs(step(case, x, lp)-lp).sum()), error_l1=float(np.abs(lp-truth).sum()),
            width_l1='', seconds=''))
    timing = []
    for n in (8, 32, 128):
        case = ring(n, .2)
        # All-default regime avoids a trivial benchmark arrested by solvent nodes.
        x = np.full(n, .1)
        reference = lp_clear(case, x)
        for name, fn in [('two_sided', lambda: bracket(case, x).payments),
                         ('residual_only', lambda: residual_only(case, x).payments),
                         ('residual_adjusted', lambda: residual_only(case, x, tolerance=1e-8*(1-case.beta)/n).payments),
                         ('LP', lambda: lp_clear(case, x))]:
            for repeat in range(3):
                p, seconds, peak = measured(fn)
                timing.append(dict(banks=n, method=name, repeat=repeat, seconds=seconds,
                                   peak_python_bytes=peak, lp_error_l1=float(np.abs(p-reference).sum()),
                                   comparable_global_accuracy=name != 'residual_only'))
    save('stress.csv', stress)
    save('payments.csv', bank_rows)
    save('weekly_regression.csv', weekly)
    save('oracles.csv', oracle_rows)
    save('near_closed.csv', near)
    save('timing.csv', timing)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), layout='constrained')
    for key, label, style, color in [('clearing_gross', 'Gross unpaid (counts repeated claims)', 'o-', '#245C83'),
        ('clearing_outside', 'Outside-creditor unpaid', 's--', '#B56A20'),
        ('one_pass_gross', 'One-pass deficit (not clearing)', 'x:', '#637843')]:
        axes[0].plot([r['haircut'] for r in stress], [r[key] for r in stress], style, color=color, label=label)
    axes[0].set(xlabel='Sovereign haircut', ylabel='Synthetic monetary units', title='Static sovereign exposure: three-bank ring')
    axes[0].legend(fontsize=8)
    accepted = [r for r in near if r['method'] == 'residual_only' and r['status'] == 'accepted']
    axes[1].loglog([r['anchor'] for r in accepted], [r['error_l1'] for r in accepted], 'o-', color='#245C83', label='Actual L1 payment error')
    axes[1].loglog([r['anchor'] for r in accepted], [r['residual_l1'] for r in accepted], 's--', color='#B56A20', label='L1 fixed-point residual')
    axes[1].set(xlabel='Outside liability share', ylabel='Synthetic monetary units', title='Residual-only stopping: negative control')
    axes[1].legend(fontsize=8)
    fig.savefig(out/'comparison.png', dpi=150)
    metadata = dict(seed=20261018, python=platform.python_version(), platform=platform.platform(),
        cpu=platform.processor(), numpy=np.__version__, tolerance_l1=1e-8,
        source_base='e25c2ac', weekly_notebook_sha256=hashlib.sha256(weekly_path.read_bytes()).hexdigest(),
        memory='tracemalloc Python allocation peak; excludes native RSS/HiGHS',
        numerical_enclosure='Floating brackets, not directed-rounding interval proof',
        hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.csv')})
    (out/'metadata.json').write_text(json.dumps(metadata, indent=2))
    (out/'config.json').write_text(json.dumps(dict(liabilities=net.liabilities.tolist(), outside=net.outside.tolist(),
        cash=cash.tolist(), sovereign=sovereign.tolist(), haircuts=np.linspace(0, 1, 11).tolist(),
        oracle_cases=30, scale_banks=[8, 32, 128], max_iterations=10000, near_anchors=[.1, .01, .001, 1e-9]), indent=2))
    print(json.dumps(dict(stress_end=stress[-1], near_end=near[-3:],
        max_oracle_error=max(r['bracket_error_l1'] for r in oracle_rows),
        max_lp_error=max(r['lp_error_l1'] for r in oracle_rows),
        max_weekly_difference=max(r['difference'] for r in weekly)), indent=2))


if __name__ == '__main__':
    main()
