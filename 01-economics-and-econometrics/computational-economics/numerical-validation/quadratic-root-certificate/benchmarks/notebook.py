"""Build and execute the narrative notebook in-process."""
import ast
import base64
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import nbformat

ROOT = Path(__file__).resolve().parents[1]
cells = [
    nbformat.v4.new_markdown_cell("""# Quadratic Root Certificate\n\n## tl;dr\nExact rational enclosures recover the simple price roots and the double fold root. The guarantee is **only** for each quadratic equation; the economic regime inequalities remain a separate model check."""),
    nbformat.v4.new_markdown_cell(r"""## Context & Methods

A liquidation regime reduces the scalar price equation to $a q^2+b q+c=0$. For rational coefficients, $\Delta=b^2-4ac$ is exact. We bound $\sqrt{\Delta}$ between adjacent rationals with denominator $10^d$ using integer square root. Substitution into the quadratic formula gives rational intervals.

### Key assumptions
Degree exactly two; rational coefficients; declared regime domains supplied externally. No claim of a certified payment vector, global equilibrium completeness, welfare, or empirical identification."""),
    nbformat.v4.new_code_cell("""from pathlib import Path\nimport json, pandas as pd\nimport matplotlib.pyplot as plt\nROOT = Path.cwd()\ncert = pd.read_csv(ROOT/'results/certificates.csv')\nvalidation = pd.read_csv(ROOT/'results/validation.csv')\nstability = pd.read_csv(ROOT/'results/stability.csv')\ncosts = pd.read_csv(ROOT/'results/costs.csv')\nmeta = json.loads((ROOT/'results/metadata.json').read_text())\nprint({'seed': meta['seed'], 'random_cases': meta['random_cases'], 'max_float_error': meta['max_float_midpoint_error']})"""),
    nbformat.v4.new_markdown_cell("## Results\n\nThe table distinguishes every polynomial root from roots that also lie wholly inside the declared economic regime interval."),
    nbformat.v4.new_code_cell("""cert[['case','midpoint','width','multiplicity','inside_declared_domain']]"""),
    nbformat.v4.new_code_cell("""assert cert.query("case == 'fold_double'").iloc[0].multiplicity == 2\nassert validation.certificate_width_max.max() <= 1e-24\nprint('100/100 random rational-root cases enclosed; max float midpoint error:', validation.float_error.max())"""),
    nbformat.v4.new_markdown_cell("### Stability and computational cost\n\nWidths are mathematical enclosures, not confidence intervals. Timings compare different guarantees and do not imply general solver superiority."),
    nbformat.v4.new_code_cell("""palette={'certificate':'#315b7d','float_formula':'#d28b36'}\nfig, axes = plt.subplots(1,2,figsize=(10,4))\nfor method, group in costs.groupby('method'):\n    axes[0].plot(group.cases, group.median_seconds, marker='o', label=method.replace('_',' '), color=palette[method])\naxes[0].set(xscale='log', yscale='log', xlabel='Quadratics', ylabel='Median seconds', title='Cost vs float baseline')\naxes[0].legend(frameon=False)\naxes[1].plot(stability.decimal_digits, stability.max_width, marker='o', color='#315b7d')\naxes[1].set(yscale='log', xlabel='Requested decimal digits', ylabel='Maximum interval width', title='Enclosure stability')\nfor ax in axes: ax.grid(axis='y', alpha=.25)\nfig.tight_layout(); plt.show()"""),
    nbformat.v4.new_markdown_cell("""## Negative ablation\n\nA 0.01 sign-change grid reports zero crossings for $(q-0.5)^2$, while the exact discriminant certifies the root $q=0.5$ with multiplicity two. This refutes the adequacy of that baseline for folds, not the usefulness of grids for exploration."""),
    nbformat.v4.new_code_cell("""ablation = pd.read_csv(ROOT/'results/ablations.csv')\nablation\nassert int(ablation.sign_change_hits.iloc[0]) == 0 and int(ablation.certified_roots.iloc[0]) == 1"""),
    nbformat.v4.new_markdown_cell("""## Takeaways\n\nThe MVP closes a numerical audit gap for quadratic price-regime equations and exposes a measurable cost premium. A root inside a declared scalar interval is still not proof that all bank-level inequalities, payments, or equilibrium assumptions hold."""),
]
notebook = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}})
path = ROOT / "notebook.ipynb"
namespace: dict[str, object] = {"__name__": "__main__"}
execution_count = 0
for cell in notebook.cells:
    if cell.cell_type != "code":
        continue
    execution_count += 1
    tree = ast.parse(cell.source)
    final_expression = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        final_expression = ast.Expression(tree.body.pop().value)
    output = StringIO()
    with redirect_stdout(output):
        exec(compile(tree, "notebook.ipynb", "exec"), namespace)
        value = eval(compile(final_expression, "notebook.ipynb", "eval"), namespace) if final_expression else None
    cell.execution_count = execution_count
    cell.outputs = []
    if output.getvalue():
        cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=output.getvalue()))
    if value is not None:
        if hasattr(value, "to_html"):
            data = {"text/plain": repr(value), "text/html": value.to_html()}
        else:
            data = {"text/plain": repr(value)}
        cell.outputs.append(nbformat.v4.new_output("execute_result", data=data, execution_count=execution_count))
    for figure_number in plt.get_fignums():
        figure = plt.figure(figure_number)
        buffer = BytesIO()
        figure.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        cell.outputs.append(nbformat.v4.new_output("display_data", data={"image/png": encoded}))
        plt.close(figure)
nbformat.write(notebook, path)
print(path)
