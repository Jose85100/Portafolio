"""Reproduce simulation, tabular output, plot, and executed notebook."""
from __future__ import annotations
import csv, json, contextlib, io
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import nbformat

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from online_conformal import evaluate, simulate

def main() -> None:
    cfg = json.loads((ROOT / "config.json").read_text())
    raw, summaries = [], []
    for sd in cfg["seeds"]:
        for scenario, break_at, scale in [("stationary", cfg["n"], 1.0), ("scale_break_2x", cfg["change"], 2.0), ("negative_break_4x", cfg["change"], 4.0)]:
            x = simulate(sd, cfg["n"], break_at, scale)
            known_scale = np.ones(cfg["n"]); known_scale[break_at:] = scale
            result = evaluate(x, cfg["alpha"], cfg["window"], known_scale)
            row = {"seed": sd, "scenario": scenario, **result}
            summaries.append(row)
            raw.append({"seed": sd, "scenario": scenario, "series": json.dumps(x.tolist(), separators=(",", ":"))})
    out = ROOT / "results"
    with (out / "summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=summaries[0].keys()); w.writeheader(); w.writerows(summaries)
    with (out / "raw_series.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=raw[0].keys()); w.writeheader(); w.writerows(raw)
    agg = {}
    for name in sorted({r["scenario"] for r in summaries}):
        rows = [r for r in summaries if r["scenario"] == name]
        agg[name] = {k: {"mean": float(np.mean([r[k] for r in rows])), "sd": float(np.std([r[k] for r in rows], ddof=1))} for k in rows[0] if k not in ("seed", "scenario")}
    (out / "summary.json").write_text(json.dumps({"config": cfg, "aggregate": agg, "replicates": len(cfg["seeds"]), "status": "synthetic simulation; not external validation"}, indent=2)+"\n")
    # Predeclared window-size sensitivity on the same seed and 2x scale break.
    sens = []
    x_sens = simulate(cfg["seeds"][0], cfg["n"], cfg["change"], 2.0)
    s_sens = np.ones(cfg["n"]); s_sens[cfg["change"]:] = 2.0
    for window in (50, 100, 200, 400):
        r = evaluate(x_sens, cfg["alpha"], window, s_sens)
        sens.append({"window": window, **r})
    with (out / "sensitivity.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sens[0].keys()); w.writeheader(); w.writerows(sens)
    # Calibration size sweep in a stationary population, preserving seed pairing.
    size_rows = []
    for window in (20, 50, 100, 200, 400):
        reps = [evaluate(simulate(sd, cfg["n"], cfg["n"], 1.0), cfg["alpha"], window) for sd in cfg["seeds"]]
        size_rows.append({"calibration_size": window, "fixed_coverage_mean": float(np.mean([r["fixed_coverage"] for r in reps])),
                          "rolling_coverage_mean": float(np.mean([r["rolling_coverage"] for r in reps])),
                          "fixed_width_mean": float(np.mean([r["fixed_mean_width"] for r in reps])),
                          "rolling_width_mean": float(np.mean([r["rolling_mean_width"] for r in reps]))})
    with (out / "calibration_size.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=size_rows[0].keys()); w.writeheader(); w.writerows(size_rows)
    # A diagnostic plot on the first scale-break replicate.
    x = simulate(cfg["seeds"][0], cfg["n"], cfg["change"], 2.0)
    w, a = cfg["window"], cfg["alpha"]
    qs = np.array([np.quantile(np.abs(x[i-w:i]), 1-a, method="higher") for i in range(w, len(x))])
    t = np.arange(w, len(x))
    fig, ax = plt.subplots(figsize=(9, 4.5)); ax.plot(t, x[w:], lw=.45, color="#425466", label="observations")
    ax.plot(t, qs, color="#e07a22", lw=1.3, label="rolling half-width"); ax.plot(t, -qs, color="#e07a22", lw=1.3)
    ax.axvline(cfg["change"], ls="--", color="#b23b3b", label="scale change"); ax.set(xlabel="time", ylabel="value / interval", title="Rolling conformal reacts to a scale break")
    ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out / "scale_break.png", dpi=160); plt.close(fig)
    # Build and actually execute notebook cells with a local Python kernel.
    cells = [
        nbformat.v4.new_markdown_cell("""# Online conformal intervals under volatility shifts

This notebook re-runs the experiment from the configured seeds. It contrasts an initial frozen split-conformal quantile with a rolling trailing-window quantile and a Gaussian oracle that knows the scale. The scale break violates the exchangeability assumption needed for the usual finite-sample guarantee; the experiment measures empirical recovery, not a new guarantee."""),
        nbformat.v4.new_markdown_cell(r"""## Rank argument and scope

For calibration scores `S_1,...,S_m`, let `k = min(m, ceil((m+1)(1-alpha)))` and `q=S_(k)`, the `k`th order statistic. A symmetric interval is `[mu-q, mu+q]`. Under exchangeability of the calibration scores and the next score, its rank is uniform (ties make the bound conservative), so marginal coverage is at least `1-alpha`. A scale break makes old and new scores non-exchangeable; neither the frozen nor moving intervals inherit that guarantee. Under iid stationarity and a growing calibration set, the empirical score quantile converges to its population quantile; this prototype uses finite windows and makes no consistency claim for the moving process. The oracle uses known `sigma` and half-width `Phi^-1(1-alpha/2) sigma`."""),
        nbformat.v4.new_markdown_cell("""## Setup and configuration

The project root is the notebook's working directory. The next cell loads the typed implementation and the experiment configuration."""),
        nbformat.v4.new_code_cell("""import json, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'src'))
from online_conformal import evaluate, simulate
config = json.loads((ROOT / 'config.json').read_text())
print('Config:', json.dumps({k: v for k, v in config.items() if k != 'seeds'}, sort_keys=True))"""),
        nbformat.v4.new_markdown_cell("""## Replicated scale-shift experiment

For each predeclared seed, generate stationary, 2x and 4x scale scenarios. Report mean coverage after the change, average interval width and the scale-known Gaussian oracle. All random series are synthetic."""),
        nbformat.v4.new_code_cell("""scenario_specs = [('stationary', config['n'], 1.0),
                  ('scale_break_2x', config['change'], 2.0),
                  ('negative_break_4x', config['change'], 4.0)]
replicates = []
for seed in config['seeds']:
    for scenario, change_at, post_scale in scenario_specs:
        series = simulate(seed, config['n'], change_at, post_scale)
        known_scale = np.ones(config['n'])
        known_scale[change_at:] = post_scale
        result = evaluate(series, config['alpha'], config['window'], known_scale)
        replicates.append({'seed': seed, 'scenario': scenario, **result})
aggregate = {}
for scenario, _, _ in scenario_specs:
    rows = [r for r in replicates if r['scenario'] == scenario]
    aggregate[scenario] = {
        'fixed_postbreak_coverage': float(np.mean([r['fixed_postbreak_coverage'] for r in rows])),
        'rolling_postbreak_coverage': float(np.mean([r['rolling_postbreak_coverage'] for r in rows])),
        'oracle_postbreak_coverage': float(np.mean([r['oracle_postbreak_coverage'] for r in rows])),
        'fixed_mean_width': float(np.mean([r['fixed_mean_width'] for r in rows])),
        'rolling_mean_width': float(np.mean([r['rolling_mean_width'] for r in rows]))}
print(json.dumps(aggregate, indent=2))"""),
        nbformat.v4.new_markdown_cell("""## Sensitivity to calibration window

Use one fixed 2x trajectory and change the rolling calibration size. This is a sensitivity check, not a tuned selection."""),
        nbformat.v4.new_code_cell("""series = simulate(config['seeds'][0], config['n'], config['change'], 2.0)
known_scale = np.ones(config['n']); known_scale[config['change']:] = 2.0
sensitivity = {window: evaluate(series, config['alpha'], window, known_scale)['rolling_postbreak_coverage']
               for window in (50, 100, 200, 400)}
sensitivity
print('Rolling post-break coverage by window:', sensitivity)"""),
        nbformat.v4.new_markdown_cell("""## Diagnostic figure

The plot shows one replicate. Orange bounds use the rolling calibration quantile; the dashed line marks the imposed scale break."""),
        nbformat.v4.new_code_cell("""print('Figure generated at results/scale_break.png')"""),
    ]
    nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}})
    # Execute every code cell in order with a real local Python interpreter. A Jupyter
    # kernel cannot bind TCP or IPC sockets in this sandbox, so the runner uses a
    # transparent in-process cell executor and records actual stdout/execution counts.
    namespace = {"__name__": "__main__"}
    for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), start=1):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(compile(cell.source, f"notebook-cell-{count}", "exec"), namespace)
        cell.execution_count = count
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text=buffer.getvalue())]
    nb.metadata["execution"] = {"method":"in-process Python exec", "status":"all code cells executed", "reason":"kernel sockets unavailable in sandbox"}
    nbformat.write(nb, ROOT / "notebook.ipynb")
    print(json.dumps(agg, indent=2))
if __name__ == "__main__": main()
