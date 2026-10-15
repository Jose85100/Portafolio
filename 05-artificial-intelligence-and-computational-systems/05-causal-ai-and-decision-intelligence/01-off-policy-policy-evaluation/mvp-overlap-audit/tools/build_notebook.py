"""Build an actually executed narrative notebook using in-process Python cells.

Avoids Jupyter kernel socket requirements in restricted runners.
"""
import contextlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
code_cells = [
    "import json, pathlib\nr = json.loads(pathlib.Path('results/summary.json').read_text())\nprint('Rows:', r['runs'], 'True policy value:', r['config']['synthetic_truth'])",
    "for regime, metrics in r['summary'].items():\n    print(regime, 'IPS RMSE:', metrics['ips']['rmse'], 'DR RMSE:', metrics['dr']['rmse'], 'ESS:', metrics['dr']['mean_ess'])",
    "for regime, metrics in r['summary'].items():\n    print(regime, 'DR low-ESS fraction:', metrics['dr']['abstention_fraction'], 'paired MSE CI:', metrics['paired_ips_minus_dr_mse_ci95'])",
    "assert r['runs'] == 720\nassert len(r['summary']) == 3\nprint('Assertions passed: raw experiment count and three regimes.')",
]
markdown = [
    "# Contextual-bandit OPE: falsifiable synthetic audit\n\nAll outputs are captured from actual Python execution. The estimators operate on **synthetic** Bernoulli rewards, not financial/customer data.",
    "## RMSE against exact DGP oracle\n\nThe target policy takes action `1-X`. Its value is exactly 0.625. IPS, DR and baselines use identical logs.",
    "## Positivity and propensity misspecification\n\nESS diagnostics are a refusal-to-claim gate, not a formal statistical confidence interval. Bootstrap CIs are across independent paired seeds.",
    "## Invariants\n\nThe test suite also checks fold leakage, determinism, invalid support and clipping bias. See `informe.md` for negative findings."
]
ns = {}
cells = []
for i, (md, code) in enumerate(zip(markdown, code_cells), start=1):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": md.splitlines(keepends=True)})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, f"<notebook-cell-{i}>", "exec"), ns)
    cells.append({"cell_type": "code", "execution_count": i, "metadata": {},
                  "source": code.splitlines(keepends=True),
                  "outputs": [{"output_type": "stream", "name": "stdout", "text": buf.getvalue().splitlines(keepends=True)}]})
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                       "language_info": {"name": "python", "version": "3.12"}}, "nbformat": 4, "nbformat_minor": 5}
(ROOT / "notebook.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Executed and captured {len(code_cells)} notebook cells")
