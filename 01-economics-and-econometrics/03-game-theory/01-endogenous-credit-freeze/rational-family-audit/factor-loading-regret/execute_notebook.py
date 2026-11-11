"""Execute notebook cells in-process and persist their visible outputs."""
from __future__ import annotations

import contextlib
import csv
import os
import io
import json
import sys
from pathlib import Path
from typing import Any

from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def markdown(source: str) -> dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code_cell(source: str, namespace: dict[str, Any], count: int) -> dict[str, Any]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(source, "<notebook-cell>", "exec"), namespace)
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": count,
        "source": source,
        "outputs": [{"output_type": "stream", "name": "stdout", "text": buffer.getvalue()}],
    }


config = json.loads((ROOT / "config.json").read_text())
rows = list(csv.DictReader((ROOT / "results/comparison.csv").open()))
summary = json.loads((ROOT / "results/summary.json").read_text())
lines = ["delta | structure | regret | threshold_exceeded", "---:|:---|---:|:---"]
lines.extend(f"{row['delta']} | {row['structure']} | {float(row['regret']):.3f} | {row['threshold_exceeded']}" for row in rows)
source_table = """import csv, json
from pathlib import Path
rows = list(csv.DictReader((Path.cwd() / 'results/comparison.csv').open()))
print('delta | structure | regret | threshold_exceeded')
print('---:|:---|---:|:---')
for row in rows:
    print(f\"{row['delta']} | {row['structure']} | {float(row['regret']):.3f} | {row['threshold_exceeded']}\")
summary = json.loads((Path.cwd() / 'results/summary.json').read_text())
print('\\nSummary:\\n' + json.dumps(summary, indent=2))"""
namespace: dict[str, Any] = {}
cells = [
    markdown("# Mixed regret under action-specific factor loadings\n\nThis is a deterministic synthetic 2x2 sensitivity exercise. It estimates no empirical behavior."),
    markdown("## Question and exact bound\nFor `u[i,j]=A[i,j]+lambda[i]*f[j]`, with `|f[j]|<=delta`, the regret bound is `max(0, max_a(g[a] + delta*abs(lambda[a]-p.lambda)*sum(q)))`. Equal loadings cancel; heterogeneous loadings leave a support term."),
    markdown("## Configured comparison\nThe notebook displays every configured sensitivity row and the analytic threshold crossing. `independent_cell_rectangular` is an adversarial ablation of the assumed error structure."),
    code_cell(source_table, namespace, 1),
]
image_source = "from pathlib import Path\nfrom IPython.display import Image, display\ndisplay(Image(filename=str(Path.cwd() / 'results/sensitivity.png')))"
InteractiveShell.instance()
with capture_output(display=True) as captured:
    exec(compile(image_source, "<notebook-image>", "exec"), {"ROOT": ROOT})
if len(captured.outputs) != 1 or "image/png" not in captured.outputs[0].data:
    raise RuntimeError("figure output was not captured")
cells.append({"cell_type": "code", "metadata": {}, "execution_count": 2, "source": image_source, "outputs": [{"output_type": "display_data", "metadata": {}, "data": captured.outputs[0].data}]})
cells.append(markdown(f"## Interpretation\nNominal regret is {summary['nominal_regret']:.3f}; the heterogeneous loading crosses the illustrative {summary['decision_threshold']:.2f} threshold at delta={summary['analytic_threshold_delta']:.5f}. This is a property of the designed example, not an empirical or equilibrium claim."))
notebook = {
    "cells": cells,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
    "nbformat": 4,
    "nbformat_minor": 4,
}
(ROOT / "notebook.ipynb").write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print("executed 2 code cells in-process; table, JSON summary, and figure outputs saved")
