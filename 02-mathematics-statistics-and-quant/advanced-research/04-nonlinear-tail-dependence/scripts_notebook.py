"""Build a genuine executed notebook; use in-process IPython without sockets."""

import argparse
from pathlib import Path

import nbformat as nb
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent


def execute_in_process(notebook):
    shell = InteractiveShell.instance()
    for i, cell in enumerate((c for c in notebook.cells if c.cell_type == "code"), 1):
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError("Notebook cell failed") from (result.error_before_exec or result.error_in_exec)
        cell.execution_count = i
        cell.outputs = []
        for name, value in (("stdout", captured.stdout), ("stderr", captured.stderr)):
            if value:
                cell.outputs.append(nb.v4.new_output("stream", name=name, text=value))
        for output in captured.outputs:
            cell.outputs.append(nb.v4.new_output("display_data", data=output.data, metadata=output.metadata))
    notebook.metadata["execution"] = {"executor": "IPython in-process; actual stdout and rich outputs"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", action="store_true")
    args = parser.parse_args()
    md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
    notebook = nb.v4.new_notebook(
        cells=[
            md(
                "# Same Kendall τ, different joint extremes\n\n## tl;dr\n"
                "Known-parameter Gaussian and Student-t copulas can have equal Kendall τ and different "
                "joint exceedance probabilities. Finite-threshold L(q) is not its asymptotic limit. "
                "This executed audit compares two quadratures and direct versus conditional Monte Carlo. "
                "All measured values below come from saved reproducible raw evidence, not forecasts."
            ),
            md(
                "## Context & Methods\n### Key Assumptions\n"
                "Bivariate IID elliptical distributions, known ρ, ν and marginal tail probability p=1−q. "
                "τ=2 arcsin(ρ)/π; L(q)=P(U>q,V>q)/(1−q). The Gaussian λ∞=0 for |ρ|<1; "
                "the t coefficient depends on ν as well as ρ. Equal rank correlation is not full model identification.\n\n"
                "### 1. Load the preregistered configuration"
            ),
            code(
                "import csv, json\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display, Image\n"
                "from src.copulas import Copula, kendall_tau, asymptotic_lambda, direct, conditional\n"
                "from src.reference import tail_coordinate_reference, conditional_second_moment\n"
                "config=json.loads(Path('config.json').read_text())\n"
                "result=json.loads(Path('benchmarks/results.json').read_text())\n"
                "print(config['question'])\nprint(json.dumps(result['checks'],indent=2))\nassert all(result['passed'].values())"
            ),
            md(
                "### 2. Verify matching rank dependence and different limits\n"
                "The t sampler uses one shared chi-square scale. At ρ=0, t components are uncorrelated "
                "but not independent; the Gaussian comparison is independent."
            ),
            code(
                "for rho in (0.,.5):\n    for df in (None,4.,30.):\n"
                "        model=Copula(rho,df)\n        print(f'rho={rho}, df={df}: tau={kendall_tau(model):.6f}; lambda_infinity={asymptotic_lambda(model):.6f}')"
            ),
            md(
                "## Data\n48 deterministic scenarios; 1,280 timed Monte Carlo runs from 80 independent "
                "replicates per cell. N=2,000 and 20,000; q=.99 and .999; ρ=.5; Gaussian/t4. "
                "No fitting on the evaluation samples. Raw seeds and counts: benchmarks/raw.csv. "
                "Numerical references: population.csv; resource peaks: memory.csv.\n\n"
                "### 3. Read finite-threshold coexceedance, not just λ∞"
            ),
            code(
                "with open('benchmarks/population.csv') as f:\n    population=list(csv.DictReader(f))\n"
                "for row in population:\n    if row['rho']=='0.5' and row['q'] in ('0.99','0.999','0.9999'):\n"
                "        print(row['model'], 'q='+row['q'], 'joint='+format(float(row['joint_probability']),'.8g'), 'L(q)='+format(float(row['finite_lambda']),'.6f'), 'limit='+format(float(row['asymptotic_lambda']),'.6f'))"
            ),
            md(
                "### 4. Recompute the variance-bound proposition\n"
                "For D=1(A∩B)/p, Var(D)=L/p−L². For H=P(B|X), X∼X|A, E[H]=L and "
                "0≤H≤1 imply Var(H)≤L(1−L). Thus Var(H)/Var(D)≤p(1−L)/(1−pL)≤p. "
                "This known conditioning argument assumes the conditional law and p are known. "
                "It is a sample-efficiency bound, not a CPU-time guarantee."
            ),
            code(
                "model=Copula(.5,4.)\nq=.999\nlam,_=tail_coordinate_reference(model,q)\n"
                "second=conditional_second_moment(model,q)\nratio=(second-lam*lam)/(lam/(1-q)-lam*lam)\n"
                "bound=(1-q)*(1-lam)/(1-(1-q)*lam)\nprint({'finite_lambda':lam,'variance_ratio':ratio,'bound':bound})\nassert ratio<=bound+1e-10"
            ),
            md(
                "## Results\n### 5. Inspect empirical accuracy, cost and zero-event failures\n"
                "RMSE is computed across all 80 replicates against the finite-q quadrature. "
                "The direct estimator is not biased downward merely because individual runs return zero. "
                "Replicate quantiles are dispersion, not confidence intervals."
            ),
            code(
                "with open('benchmarks/summary.csv') as f:\n    summary=list(csv.DictReader(f))\n"
                "for row in summary:\n    if row['model']=='t4' and row['q']=='0.999':\n"
                "        print({k:row[k] for k in ('n','method','relative_rmse','mean_seconds','zero_joint_fraction','undefined_random_denominator','time_times_mse_proxy')})"
            ),
            md(
                "### 6. Recompute one independent illustration\n"
                "This is an extra illustrative draw, not a replacement for the full replication benchmark. "
                "N is equal, but inverse-quantile and conditional-CDF costs differ."
            ),
            code(
                "for name,method,seed in [('direct',direct,1801),('conditional',conditional,1802)]:\n"
                "    estimate=method(Copula(.5,4.),.999,20000,np.random.default_rng(seed))\n"
                "    print(name,estimate)"
            ),
            md(
                "### 7. Inspect the summary figure\n"
                "Left: finite-q quadrature versus dashed limits. Right: observed RMSE at equal N, not equal runtime."
            ),
            code("display(Image(filename='benchmarks/audit.png'))"),
            md("### 8. Check sampler rank diagnostics and numerical residuals"),
            code(
                "with open('benchmarks/rank_check.csv') as f:\n    print(list(csv.DictReader(f)))\n"
                "print('max quadrature disagreement:',result['checks']['max_quadrature_disagreement'])\n"
                "print('All gates passed:', all(result['passed'].values()))"
            ),
            md(
                "## Takeaways\n"
                "Matching central rank dependence does not identify joint tail behavior. Gaussian asymptotic "
                "independence is not finite-threshold independence; a t limit is also not an exact finite-q "
                "probability. Conditioning improves precision in the declared synthetic experiment, at a different "
                "per-sample cost.\n\n"
                "Limits: known parameters, symmetric families, no temporal dependence, no calibration of estimated "
                "copulas, no coverage study and no financial capital validation. The two quadratures share SciPy; "
                "agreement is not formal certification. See informe.md, config.json and referencias.bib for the "
                "derivation, raw negative outcomes, references and scope."
            ),
        ]
    )
    notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.validate(notebook)
    if args.kernel:
        NotebookClient(
            notebook, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        notebook.metadata["execution"] = {"executor": "nbclient conventional kernel"}
    else:
        execute_in_process(notebook)
    nb.validate(notebook)
    nb.write(notebook, ROOT / "notebook.ipynb")
    print("Executed and saved all eight code cells with outputs.")


if __name__ == "__main__":
    main()
