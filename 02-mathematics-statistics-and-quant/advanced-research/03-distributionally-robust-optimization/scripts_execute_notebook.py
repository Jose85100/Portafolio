"""Actually execute standard Python notebook cells and retain rich/text outputs."""

from pathlib import Path
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parent
nb = nbformat.v4.new_notebook(
    cells=[
        nbformat.v4.new_markdown_cell(
            "# KL robust expectations: approximation is not a bound\n\nFinite probabilities p_i>0 and KL(q||p)<=rho. A centered log-domain exponential tilt solves the scalar KL boundary, with explicit nominal, constant-loss and saturation cases. Compare a primal SLSQP baseline, a small-radius mean-variance approximation, and an independent Bernoulli oracle. Established methods; this is not Wasserstein DRO or a calibrated confidence region."
        ),
        nbformat.v4.new_code_cell(
            "import json\nfrom pathlib import Path\nr=json.loads(Path('benchmarks/results.json').read_text())\nprint('Predeclared gate:',r['success'])\nprint('Checks:',r['checks'])\nprint('Cases:',r['cases'])\nprint('SLSQP rejected:',len(r['rejected_slsqp']))\nfor row in r['summary']:\n    print(row)"
        ),
        nbformat.v4.new_code_cell(
            "print('Two-action example (0=risky, 1=safe):')\nfor key,value in r['decision'].items():\n    print(key,value)\nassert r['decision']['mean_variance_risky_loss']<r['decision']['safe_loss']<r['decision']['exact_robust_risky_loss']"
        ),
        nbformat.v4.new_code_cell(
            "from IPython.display import Image,display\ndisplay(Image(filename='benchmarks/audit.png'))"
        ),
        nbformat.v4.new_code_cell(
            "initial=json.loads(Path('benchmarks/initial_baseline/results.json').read_text())\nprint('Initial baseline experiment passed?',initial['success'])\nprint(initial['checks'])\nassert initial['success'] is False\nprint('Initial failed experiment retained; thresholds were not relaxed.')"
        ),
        nbformat.v4.new_markdown_cell(
            "## Conclusions and limits\n\nThe mean-variance small-radius expansion can underestimate a rare-event robust loss and change a minimax decision. It is an approximation, not a global upper bound. Robustness can cost nominal performance; both explicit scenarios are retained. Radius and support are assumed known, not estimated. The initial SLSQP configuration failed the global gate and is preserved. A stronger interior two-start configuration is compared without changing thresholds. Bounds are float64 diagnostics, not formal interval-arithmetic certificates or financial capital guarantees."
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
print("Four code cells actually executed with visible outputs.")
