"""Build and actually execute the notebook with the active Python interpreter."""

import sys
from pathlib import Path
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parent

nb = nbformat.v4.new_notebook(
    cells=[
        nbformat.v4.new_markdown_cell(
            "# Disconnected Gaussian tails — S2 prototype\n\nEstimate P(|X|>a), X~N(0,1). Compare direct MC, N(a,1), a balanced two-tail mixture, and a 10% defensive mixture. Ordinary IS uses the full mixture density; it is not self-normalized. See informe.md for prior art and assumptions."
        ),
        nbformat.v4.new_code_cell(
            "import json, csv\nfrom pathlib import Path\nfrom src.estimators import truth, population_variance\nr = json.loads(Path('benchmarks/results.json').read_text())\nprint('Success gate:', r['success'])\nprint('RMSE ratio:', r['rmse_ratio'])\nfor name, row in r['selected'].items():\n    print(name, 'mean=', row['mean'], 'relative RMSE=', row['relative_rmse'], 'coverage=', row['coverage_95'])"
        ),
        nbformat.v4.new_code_cell(
            "from IPython.display import Image, display\ndisplay(Image(filename='benchmarks/rmse.png'))"
        ),
        nbformat.v4.new_code_cell(
            "a=4.0\nfor m in ['direct','single_tilt','balanced','defensive']:\n    print(m, 'true per-draw variance:', population_variance(a,m))\nprint('Exact event probability:', truth(a))"
        ),
        nbformat.v4.new_markdown_cell(
            "## Conclusions\nA proposal shifted to one tail remains unbiased in expectation but misses the other tail in finite samples and can report misleadingly small standard errors. The balanced mixture is a known remedy, not a new algorithm. Forty replications do not establish coverage calibration. This univariate synthetic experiment does not validate financial capital estimates or high-dimensional performance."
        ),
    ]
)
nb.metadata["kernelspec"] = {
    "name": "rare-event-mvp",
    "display_name": "Rare event MVP",
    "language": "python",
}
# In-process execution avoids TCP kernel startup in restricted environments.
# Every cell really runs; captured text and rich display outputs are serialized.
shell = InteractiveShell.instance()
nb.metadata["execution"] = {"executor": "IPython in-process", "python": sys.version}
for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), 1):
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError("Notebook cell failed") from (
            result.error_before_exec or result.error_in_exec
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
nbformat.write(nb, root / "notebook.ipynb")
print("Notebook executed using", sys.executable)
