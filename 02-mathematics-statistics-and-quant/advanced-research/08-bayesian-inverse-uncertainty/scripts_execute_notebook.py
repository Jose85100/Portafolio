"""Execute every notebook code cell in-process and retain actual rich/text outputs."""

from pathlib import Path
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parent
nb = nbformat.v4.new_notebook(
    cells=[
        nbformat.v4.new_markdown_cell(
            "# Linear Gaussian inverse problem: numerical and statistical audits\n\nThe posterior is analytic. SVD and augmented QR avoid explicitly forming a squared-condition normal-equations matrix. Their accuracy is compared to an 80-digit oracle for the actual rounded inputs. Calibration is tested separately under the joint prior-predictive distribution. This is established methodology, not a new inference algorithm."
        ),
        nbformat.v4.new_code_cell(
            "import json\nfrom pathlib import Path\nreport=json.loads(Path('benchmarks/results.json').read_text())\nprint('Predeclared gate:', report['success'])\nprint('SVD versus QR:', report['max_svd_qr_difference'])\nfor row in report['selected']:\n    print(row['d'],row['method'],'median relative mean error',row['median_mean_relative_error'],'failures',row['failed'])"
        ),
        nbformat.v4.new_code_cell(
            "for row in report['calibration']:\n    print(row['scenario'], row['direction'], 'coverage=',row['coverage_95'], 'Wilson 95% interval=',(row['coverage_wilson_low'],row['coverage_wilson_high']))"
        ),
        nbformat.v4.new_code_cell(
            "from IPython.display import Image,display\ndisplay(Image(filename='benchmarks/audit.png'))"
        ),
        nbformat.v4.new_code_cell(
            "import numpy as np\nfrom src.posterior import posterior\na=np.diag([1.,.01,0.])\np=posterior(a,np.array([1.,.1,10.]),sigma=.1,tau=2.)\nprint('Mean:',p.mean)\nprint('Posterior variances:',np.diag(p.covariance))\nassert abs(p.covariance[-1,-1]-4)<1e-12\nprint('The unobserved direction retains the prior variance.')"
        ),
        nbformat.v4.new_markdown_cell(
            "## Conclusions and limits\n\nNormal equations can lose accuracy despite small residuals. SVD is compared to a strong QR baseline: no universal superiority is asserted. A stable posterior still has poor coverage under an understated noise level or overly concentrated prior. Coverage here averages over draws of theta from the prior; it is not a fixed-theta frequentist guarantee. Dense finite-dimensional isotropic Gaussian assumptions exclude nonlinear operators, empirical financial calibration and model discrepancy inference."
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
print("Four code cells actually executed; notebook saved with outputs.")
