"""Build and actually execute the notebook, preserving real text and rich outputs."""

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
    notebook.metadata["execution"] = {"executor": "IPython in-process, actual executed cells and outputs"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", action="store_true")
    args = parser.parse_args()
    md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
    notebook = nb.v4.new_notebook(
        cells=[
            md(
                "# Fractional difference: small weights can leave a large tail\n\n## tl;dr\n"
                "This audit separates truncation error, floating-point agreement and initialization. "
                "An individual coefficient threshold is not a bound on accumulated error; a finite-horizon "
                "tail-mass budget is. Full direct and properly padded FFT are numerical baselines. "
                "All empirical values below come from executed artifacts, not claims about economic memory."
            ),
            md(
                "## Context & Methods\n### Key Assumptions\n"
                "Discrete y(t)=Σ w(k)x(t−k), w(k)=(−1)^k binom(d,k), step one. "
                "0<d<1, zero extension for negative t, known finite horizon N and bounded input. "
                "This is not automatically a Caputo derivative, stationary infinite-past filter or a test for long memory.\n\n"
                "### 1. Load the configuration and execution checks"
            ),
            code(
                "import csv, json\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display, Image\n"
                "from src.fractional import weights, tail_masses, coefficient_memory, budget_memory, apply_filter\n"
                "from src.reference import prefix_gamma, oracle_filter\n"
                "config=json.loads(Path('config.json').read_text())\n"
                "result=json.loads(Path('benchmarks/results.json').read_text())\n"
                "print(config['question'])\nprint(json.dumps(result['checks'],indent=2))\nassert all(result['passed'].values())"
            ),
            md(
                "### 2. Verify the weights and Gamma prefix\n"
                "w₀=1; wₖ=wₖ₋₁(k−1−d)/k. For 0<d<1 the remaining weights are negative. "
                "The prefix rₘ=Γ(m+1−d)/[Γ(1−d)Γ(m+1)] is positive and tends to zero slowly."
            ),
            code(
                "w=weights(.4,64)\nprint('first weights:',w[:6])\n"
                "for m in (0,1,7,63):\n    print('m=',m,'sum=',float(w[:m+1].sum()),'Gamma oracle=',prefix_gamma(.4,m))\n"
                "assert np.all(w[1:]<0)"
            ),
            md(
                "## Data\n36 scenarios: three d, three lengths and four bounded input families. "
                "The 12 unique input series are saved in benchmarks/inputs.npz; d changes the filter, not the input. "
                "216 method results and 648 timing records. Three timing repetitions are not independent statistical "
                "replicates. Config and CSVs record seeds, memory indexing and timing scope.\n\n"
                "### 3. Recompute the coefficient-cutoff counterexample"
            ),
            code(
                "n=8192\nd=.4\nx=np.ones(n)\nw=weights(d,n)\nm=coefficient_memory(w,.001)\n"
                "full=apply_filter(x,w)\ncut=apply_filter(x,w,m)\n"
                "error=float(np.max(np.abs(cut-full)))\n"
                "print({'retained_max_lag':m,'first_discarded_weight':float(w[m+1]),'max_error':error,'tail_bound':float(tail_masses(w)[m]),'error_over_epsilon':error/.001})\n"
                "assert abs(w[m+1])<=.001 and error>20*.001"
            ),
            md(
                "### 4. Verify the finite-horizon error proposition\n"
                "For |x|≤M, truncating after m gives |error(t)|≤MΣ(k=m+1..t)|wₖ|≤M T(m,N). "
                "Because all omitted weights share a sign, T(m,N)=rₘ−r(N−1). A constant unit input "
                "attains the bound at the last time. The selector chooses the smallest m with T≤η. "
                "The bound is relative to input scale, not to an output that may be nearly zero."
            ),
            code(
                "for d in config['grid']['d']:\n    w=weights(d,8192)\n    m=budget_memory(w,.01)\n"
                "    tail=tail_masses(w)\n    y=apply_filter(np.ones(8192),w,m)\n    yfull=apply_filter(np.ones(8192),w)\n"
                "    err=float(np.max(np.abs(y-yfull)))\n"
                "    print({'d':d,'memory':m,'retained_fraction':(m+1)/8192,'error':err,'bound':float(tail[m])})\n"
                "    assert err<=.0100000001\n    assert m==0 or tail[m-1]>.01"
            ),
            md(
                "## Results\n### 5. Inspect accuracy and cost together\n"
                "Timing includes validation/filtering, excludes weight/selector setup, and uses fixed order. "
                "Setup is recorded separately. Peak tracked allocation is not process RSS. "
                "Do not infer universal speed superiority from these local measurements."
            ),
            code(
                "with open('benchmarks/summary.csv') as f:\n    summary=list(csv.DictReader(f))\n"
                "for row in summary:\n    if row['family']=='ar1' and row['d']=='0.4' and row['method'] in ('full_direct','full_fft','tail_budget'):\n"
                "        print({k:row[k] for k in ('n','method','memory','scaled_error','median_seconds','tracked_peak_bytes')})"
            ),
            md(
                "### 6. Distinguish boundary assumptions from numerical error\n"
                "A full zero-extended unit constant has output r(t), not zero. "
                "Circular FFT without padding wraps a future end-pulse into the start; this deliberately "
                "incorrect ablation is not a competitive baseline."
            ),
            code(
                "z=np.zeros(64)\nz[-1]=1\nw=weights(.4,64)\n"
                "linear=apply_filter(z,w,method='fft')\ncircular=np.fft.irfft(np.fft.rfft(z)*np.fft.rfft(w),n=64)\n"
                "print({'linear_at_start':float(linear[0]),'circular_at_start':float(circular[0]),'zero_extended_constant_at_last':prefix_gamma(.4,8191)})\n"
                "assert abs(linear[0])<1e-12 and abs(circular[0])>.1"
            ),
            md(
                "### 7. Inspect the three-part figure\n"
                "Left: accumulated error on the unit constant. Middle: fraction of retained coefficients, "
                "not total-program memory savings. Right: full-history direct and linear FFT timings."
            ),
            code("display(Image(filename='benchmarks/audit.png'))"),
            md(
                "### 8. Recompute a short-series high-precision reference\n"
                "The reference uses mpmath binomial special functions and 80-digit summation, "
                "not the same float recurrence. It is deliberately limited to short inputs."
            ),
            code(
                "x=np.random.default_rng(191905).uniform(-1,1,64)\nw=weights(.4,len(x))\n"
                "ref=oracle_filter(x,.4)\n"
                "print({'direct_vs_80_digits':float(np.max(np.abs(apply_filter(x,w)-ref))),'fft_vs_80_digits':float(np.max(np.abs(apply_filter(x,w,method='fft')-ref)))})\n"
                "assert np.max(np.abs(apply_filter(x,w)-ref))<1e-11"
            ),
            md(
                "## Takeaways\n"
                "A coefficient threshold can leave a large accumulated tail. The finite-horizon budget "
                "controls truncation under bounded inputs; small d may require almost full history. "
                "FFT needs padding to preserve linear convolution. Initialization is part of the model.\n\n"
                "Limits: scalar discrete operator, fixed known d/N, float64 verification rather than formal "
                "interval certification. No Hurst estimation, distinction between economic long memory and breaks, "
                "streaming implementation, continuous fractional SDE or financial validation. "
                "See informe.md, referencias.bib and fuentes.md for derivations, prior art and source-access limits."
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
    print("Eight code cells actually executed and saved with outputs.")


if __name__ == "__main__":
    main()
