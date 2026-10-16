"""Run standard Python notebook cells in-process; capture real text and rich outputs."""

from pathlib import Path
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parent
nb = nbformat.v4.new_notebook(
    cells=[
        nbformat.v4.new_markdown_cell(
            "# Optimal transport: feasibility before cost\n\nFinite balanced transport with cost C_ij=(x_i-y_j)^2. Compare direct Sinkhorn, log-domain Sinkhorn and unregularized HiGHS LP. An independent 1D weighted monotone coupling verifies LP costs. Rounding repairs feasibility, not entropy bias or optimality. Numerical primal-dual bounds are checked with float64 tolerances; they are not interval-arithmetic certificates."
        ),
        nbformat.v4.new_code_cell(
            "import json\nfrom pathlib import Path\nr=json.loads(Path('benchmarks/results.json').read_text())\nprint('Predeclared gate:',r['success'])\nprint('Checks:',r['checks'])\nprint('Summary:',r['summary'])"
        ),
        nbformat.v4.new_code_cell(
            "print('Two-atom adversarial experiment:')\nfor name,value in r['adversarial'].items():\n    print(name,value)\nassert r['adversarial']['raw_residual']>1\nassert abs(r['adversarial']['rounded_cost']-.8)<1e-12"
        ),
        nbformat.v4.new_code_cell(
            "print('n=64, epsilon=.005:')\nfor row in r['selected']:\n    print(row['scenario'],row['method'],'failure:',row['failed'],'LP:',row['reference'],'repaired cost:',row['upper'],'converged:',row['converged'])"
        ),
        nbformat.v4.new_code_cell(
            "from IPython.display import Image,display\ndisplay(Image(filename='benchmarks/audit.png'))"
        ),
        nbformat.v4.new_markdown_cell(
            "## Conclusions\n\nA near-zero cost may be infeasible and is not evidence of an improved transport solver. Log-domain updates avoid the observed kernel underflow, but do not ensure fast convergence. Feasible rounding gives an upper bound, not the exact optimum; entropy and early-stopping errors remain. One-dimensional synthetic cases do not establish multivariate performance or causal distributional dynamics. See informe.md for assumptions, prior art, raw failures and limitations."
        ),
    ]
)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata["execution"] = {"executor": "IPython in-process", "python": sys.version}
shell = InteractiveShell.instance()
for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), 1):
    with capture_output() as captured:
        outcome = shell.run_cell(cell.source, store_history=False)
    if outcome.error_before_exec or outcome.error_in_exec:
        raise RuntimeError("Notebook execution failed") from (
            outcome.error_before_exec or outcome.error_in_exec
        )
    cell.execution_count = count
    cell.outputs = []
    for stream, value in [("stdout", captured.stdout), ("stderr", captured.stderr)]:
        if value:
            cell.outputs.append(nbformat.v4.new_output("stream", name=stream, text=value))
    for output in captured.outputs:
        cell.outputs.append(
            nbformat.v4.new_output("display_data", data=output.data, metadata=output.metadata)
        )
nbformat.validate(nb)
nbformat.write(nb, ROOT / "notebook.ipynb")
print("Four code cells executed with visible outputs.")
