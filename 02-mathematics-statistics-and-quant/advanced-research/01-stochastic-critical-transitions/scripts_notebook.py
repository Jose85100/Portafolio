"""Execute genuine IPython cells without sockets; --kernel uses nbclient instead."""

import argparse
from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent


def execute_in_process(notebook):
    """Capture actual stdout and display_data; abort on every cell error."""
    shell = InteractiveShell.instance()
    for count, cell in enumerate((c for c in notebook.cells if c.cell_type == "code"), 1):
        with capture_output() as captured:
            outcome = shell.run_cell(cell.source, store_history=False)
        if outcome.error_before_exec or outcome.error_in_exec:
            raise RuntimeError("Notebook cell failed") from (
                outcome.error_before_exec or outcome.error_in_exec
            )
        cell.execution_count = count
        cell.outputs = []
        for stream, value in (("stdout", captured.stdout), ("stderr", captured.stderr)):
            if value:
                cell.outputs.append(nbf.v4.new_output("stream", name=stream, text=value))
        for output in captured.outputs:
            cell.outputs.append(nbf.v4.new_output("display_data", data=output.data, metadata=output.metadata))
    notebook.metadata["execution"] = {
        "executor": "IPython in-process; real cells and rich outputs, no sockets"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kernel", action="store_true", help="Use a conventional Jupyter kernel (needs local sockets)"
    )
    args = parser.parse_args()
    notebook = nbf.v4.new_notebook()
    notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    notebook.cells = [
        nbf.v4.new_markdown_cell(
            "# OU audit: noise is not slowing\n\n## tl;dr\n"
            "Finite-step, known-zero-mean Ornstein–Uhlenbeck episodes separate numerical bias "
            "from statistical identification. The stationary variance can increase identically "
            "under slower recovery and under larger noise. No tipping event is forecast here. "
            "The executed cells below provide the measured evidence and limitations."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n"
            "Question: can variance identify slowing, and does Euler preserve the OU law?\n\n"
            "### Key Assumptions\n"
            "Scalar dX = −κX dt + σdW, κ>0, known mean zero, regular noiseless observation, "
            "stationary episodes with independent replicates within cells and paired mechanisms. φ=exp(−κΔt), q=σ²(1−exp(−2κΔt))/(2κ). "
            "Euler uses φ=1−κΔt, q=σ²Δt. Its stationary law requires 0<κΔt<2. "
            "Baselines and seeds were fixed in config.json. All references: referencias.bib.\n\n"
            "### 1. Load configuration and saved audit"
        ),
        nbf.v4.new_code_cell(
            "import csv, json\nfrom pathlib import Path\nimport numpy as np\n"
            "from IPython.display import display, Image\nfrom src.ou import exact_transition, euler_transition, stationary_variance\n"
            "config = json.loads(Path('config.json').read_text())\n"
            "result = json.loads(Path('benchmarks/results.json').read_text())\n"
            "print(json.dumps({'question': config['question'], 'checks': result['checks'], 'passed': result['passed']}, indent=2))\n"
            "assert all(result['passed'].values())"
        ),
        nbf.v4.new_markdown_cell(
            "## Data\n"
            "84 simulations: seven step sizes × two sample counts × three seeds × two methods; "
            "40 steps from X0=0 (horizon changes with Δt and is recorded). "
            "3,200 stationary episode records: two mechanisms × four levels × two lengths "
            "× 200 replicates; standardized innovations are paired between mechanisms. "
            "No trajectories selected by realized collapse. Raw rows: benchmarks/*.csv. "
            "Representative paths: example_paths.npz; full draws regenerate from seeds.\n\n"
            "### 2. Recompute the population counterexample"
        ),
        nbf.v4.new_code_cell(
            "for level in config['identification']['kappa_levels']:\n"
            "    slow = exact_transition(level, 1., 1.)\n"
            "    noise = exact_transition(1., np.sqrt(1/level), 1.)\n"
            "    assert np.isclose(stationary_variance(slow), stationary_variance(noise))\n"
            "    print(f'level={level:.1f}: variance={stationary_variance(slow):.6f}; phi_slow={slow.phi:.6f}; phi_noise={noise.phi:.6f}')\n"
            "print('Euler/exact stationary variance at kappa*dt=1:', stationary_variance(euler_transition(1.,1.,1.))/stationary_variance(exact_transition(1.,1.,1.)))"
        ),
        nbf.v4.new_markdown_cell(
            "## Results\n### 3. Review finite-sample dispersion\n"
            "Known-mean second moment and conditional OLS coefficient are not sample-demeaned Pearson "
            "statistics. Undefined logarithmic rates are counted, not clipped or silently dropped."
        ),
        nbf.v4.new_code_cell(
            "with open('benchmarks/summary.csv') as f:\n    summary = list(csv.DictReader(f))\n"
            "for row in summary:\n    if row['level']=='0.1':\n        print({k:row[k] for k in ('family','length','variance_median','phi_median','kappa_median_valid_only','undefined_rate_count')})\n"
            "print('Undefined rates across all episodes:', result['undefined_rates'])"
        ),
        nbf.v4.new_markdown_cell(
            "### 4. Inspect the numerical and statistical comparison\n"
            "Left: exact finite-horizon second moments relative to the OU oracle, not Monte Carlo estimates. "
            "Middle: population variances coincide. Right: empirical 2.5–97.5% replicate quantiles "
            "at length 256, not confidence intervals for a population parameter."
        ),
        nbf.v4.new_code_cell("display(Image(filename='benchmarks/audit.png'))"),
        nbf.v4.new_markdown_cell(
            "## Takeaways\n"
            "Variance alone does not identify recovery loss even at population level. Under these strong "
            "OU assumptions, lag-1 information can distinguish the two mechanisms. A coarse Euler step "
            "can double stationary variance, induce negative lag-1 correlation, or remove stationarity.\n\n"
            "Limits: no nonlinear bifurcation, colored forcing, measurement noise, parameter drift, "
            "CUSUM comparison, prospective false-alarm calibration or financial validation. "
            "The population counterexample is algebraic; the simulation illustrates, not proves, "
            "its generalization to unknown processes. See informe.md for failures and resource caveats."
        ),
    ]
    nbf.validate(notebook)
    if args.kernel:
        NotebookClient(
            notebook, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        notebook.metadata["execution"] = {"executor": "nbclient conventional Jupyter kernel"}
    else:
        execute_in_process(notebook)
    nbf.validate(notebook)
    assert all(c.execution_count is not None for c in notebook.cells if c.cell_type == "code")
    nbf.write(notebook, ROOT / "notebook.ipynb")
    print("Notebook executed top-to-bottom: 4 code cells with saved outputs.")


if __name__ == "__main__":
    main()
