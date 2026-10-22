"""Build and execute the narrative notebook without an external kernel."""

import ast
import base64
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import nbformat

ROOT = Path(__file__).resolve().parents[1]
cells = [
    nbformat.v4.new_markdown_cell(
        """# Collateral Liquidity Choice\n\n## tl;dr\nFor the main synthetic balance sheet, a collateral-constrained mix uses less liquidation and lower private funding cost than liquidation-only. This is a one-bank optimization result—not a network equilibrium, policy recommendation, or welfare estimate."""
    ),
    nbformat.v4.new_markdown_cell(r"""## Context & Methods

The bank covers shortfall $g$ by selling $x$ units at terminal price $q(x)=\max(\underline q,q_0-a x)$ and borrowing $\ell=[g-q(x)x]^+$. Borrowing obeys $\ell\leq\theta q(x)(s-x)$. Private reduced-form cost is $(q_0-q(x))x+r\ell$.

### Key assumptions
One bank, one asset, simultaneous terminal-price proceeds, exogenous pledgeable fraction and borrowing rate, no default option, network, strategic lender, margin feedback, government, data, identification, or welfare function."""),
    nbformat.v4.new_code_cell(
        """from pathlib import Path\nimport json, pandas as pd\nimport matplotlib.pyplot as plt\nROOT=Path.cwd()\nmain=pd.read_csv(ROOT/'results/main_results.csv')\nsens=pd.read_csv(ROOT/'results/sensitivity.csv')\nstability=pd.read_csv(ROOT/'results/stability.csv')\ncosts=pd.read_csv(ROOT/'results/costs.csv')\nmeta=json.loads((ROOT/'results/metadata.json').read_text())\nprint({'seed':meta['seed'],'random_cases':meta['random_cases'],'max_grid_cost_gap':meta['max_grid_cost_gap']})"""
    ),
    nbformat.v4.new_markdown_cell(
        "## Results\n\nThe dense grid is an independent numerical baseline. Liquidation-only is the economic baseline."
    ),
    nbformat.v4.new_code_cell(
        """main[['method','liquidation','borrowing','price','cost','collateral_slack']]"""
    ),
    nbformat.v4.new_code_cell(
        """opt=main.query("method=='collateral_choice'").iloc[0]\npure=main.query("method=='liquidation_only'").iloc[0]\nassert opt.cost < pure.cost and opt.borrowing > 0\nprint('relative private-cost reduction:', 1-opt.cost/pure.cost)"""
    ),
    nbformat.v4.new_markdown_cell(
        "### Sensitivity and cost\n\nLines are deterministic scenarios, not confidence intervals. A lower private cost is not necessarily lower systemic cost."
    ),
    nbformat.v4.new_code_cell(
        """fig,axes=plt.subplots(1,2,figsize=(10,4))\npalette={.05:'#315b7d',.1:'#d28b36',.5:'#7b8f35',2:'#9b5c7a'}\nfor rate,color in palette.items():\n    sub=sens.query('rate == @rate').dropna()\n    axes[0].plot(sub.pledgeable,sub.liquidation,marker='o',label=f'rate={rate:g}',color=color)\naxes[0].set(xlabel='Pledgeable fraction',ylabel='Optimal liquidation',title='Funding mix by collateral capacity')\naxes[0].legend(frameon=False)\naxes[1].plot(stability.points,stability.cost_error,marker='o',color='#315b7d')\naxes[1].set(xscale='log',yscale='log',xlabel='Grid points',ylabel='Cost error',title='Dense-grid convergence')\nfor ax in axes: ax.grid(axis='y',alpha=.25)\nfig.tight_layout(); plt.show()"""
    ),
    nbformat.v4.new_markdown_cell("""## Negative ablations

Abundant collateral alone still produces a mixed choice because positive-rate borrowing has a cost. Free borrowing selects borrowing-only; a high borrowing rate and zero price impact select liquidation. Hence “more collateral eliminates sales” is false under a positive funding price and this private objective."""),
    nbformat.v4.new_code_cell(
        """pd.read_csv(ROOT/'results/ablations.csv')[['scenario','liquidation','borrowing','price','cost']]"""
    ),
    nbformat.v4.new_markdown_cell("""## Takeaways

The candidate solver exposes the collateral boundary and agrees with dense grids while being much cheaper at scale. It advances a narrow S2 component; network equilibrium, strategic guarantees, empirical identification and welfare remain open."""),
]
notebook = nbformat.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        }
    },
)
namespace: dict[str, object] = {"__name__": "__main__"}
count = 0
for cell in notebook.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    tree = ast.parse(cell.source)
    final = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        final = ast.Expression(tree.body.pop().value)
    stream = StringIO()
    with redirect_stdout(stream):
        exec(compile(tree, "notebook.ipynb", "exec"), namespace)
        value = (
            eval(compile(final, "notebook.ipynb", "eval"), namespace) if final else None
        )
    cell.execution_count = count
    cell.outputs = []
    if stream.getvalue():
        cell.outputs.append(
            nbformat.v4.new_output("stream", name="stdout", text=stream.getvalue())
        )
    if value is not None:
        data = {"text/plain": repr(value)}
        if hasattr(value, "to_html"):
            data["text/html"] = value.to_html()
        cell.outputs.append(
            nbformat.v4.new_output("execute_result", data=data, execution_count=count)
        )
    for number in plt.get_fignums():
        figure = plt.figure(number)
        buffer = BytesIO()
        figure.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
        cell.outputs.append(
            nbformat.v4.new_output(
                "display_data",
                data={"image/png": base64.b64encode(buffer.getvalue()).decode("ascii")},
            )
        )
        plt.close(figure)
path = ROOT / "notebook.ipynb"
nbformat.write(notebook, path)
print(path)
