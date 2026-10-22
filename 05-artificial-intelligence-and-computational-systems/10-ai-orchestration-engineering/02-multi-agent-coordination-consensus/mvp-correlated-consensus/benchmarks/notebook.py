"""Execute notebook code cells in-process; persist actual stdout as notebook outputs.

This avoids Jupyter kernel sockets in constrained runners. It does not claim a
Jupyter kernel was started. A standard notebook reader can display outputs.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = [
    ("# Purpose and experiment", "from src.consensus import REGIMES, POLICIES\nprint('Regimes:', REGIMES)\nprint('Policies:', POLICIES)"),
    ("# The vote aggregation equation", "from src.consensus import decide\nvotes=(0,0,0,1,1)\nweights=(1.1,1.1,1.1,1.5,1.5)\nfor policy in POLICIES:\n    print(policy, decide(votes,weights,policy))"),
    ("# Measured risk, no hard-coded values", "import json\nfrom pathlib import Path\ns=json.loads(Path('results/summary.json').read_text())['summary']\nfor regime in REGIMES:\n    print(regime, {p: s[regime][p]['risk_at_80'] for p in POLICIES})"),
    ("# Negative controls and paired uncertainty", "x=json.loads(Path('results/summary.json').read_text())\nfor regime, result in x['paired_bootstrap'].items():\n    print(regime, result)\nassert x['summary']['shared_failure']['weighted']['risk_at_80'] == x['summary']['shared_failure']['wrong_metadata']['risk_at_80']"),
]


def build() -> None:
    ns: dict = {}
    cells = [{"id": "intro", "cell_type": "markdown", "metadata": {}, "source": ["# Correlated-agent consensus audit\n",
              "Synthetic evidence only. Group labels are assumed known; confidence margins are not probabilities.\n"]}]
    for i, (heading, code) in enumerate(CELLS, start=1):
        cells.append({"id": f"section-{i}", "cell_type": "markdown", "metadata": {}, "source": [f"## {heading}\n"]})
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exec(compile(code, f"<notebook-cell-{i}>", "exec"), ns)
        output = stdout.getvalue()
        if not output:
            raise RuntimeError(f"Cell {i} had no observable output")
        cells.append({"id": f"code-{i}", "cell_type": "code", "execution_count": i, "metadata": {}, "source": code.splitlines(True),
                      "outputs": [{"output_type": "stream", "name": "stdout", "text": output.splitlines(True)}]})
    notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}, "execution_method": "in-process Python exec; not a Jupyter kernel"},
                "nbformat": 4, "nbformat_minor": 5}
    (ROOT / "notebook.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Executed {len(CELLS)} code cells in-process; outputs saved to notebook.ipynb")


if __name__ == "__main__":
    build()
