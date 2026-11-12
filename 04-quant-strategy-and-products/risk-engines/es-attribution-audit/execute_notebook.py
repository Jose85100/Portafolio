"""Execute notebook code cells in-process and save inspectable outputs.

This avoids requiring a Jupyter kernel/socket. Code cells run as Python source in
one shared namespace; plot output is embedded from the deterministic PNG.
"""
from __future__ import annotations

import base64
import contextlib
import io
import json
from pathlib import Path
from typing import Any


def execute() -> None:
    root = Path(__file__).resolve().parent
    notebook_path = root / "notebook.ipynb"
    notebook: dict[str, Any] = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace: dict[str, Any] = {"__name__": "__main__"}
    execution_count = 0
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        execution_count += 1
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            # The notebook is this package's trusted, version-controlled source.
            exec(compile("".join(cell["source"]), f"notebook-cell-{execution_count}", "exec"), namespace)  # noqa: S102
        cell["execution_count"] = execution_count
        cell["outputs"] = []
        captured = output.getvalue()
        if captured:
            cell["outputs"].append({"output_type": "stream", "name": "stdout", "text": captured})
        if "display_figure" in cell.get("metadata", {}).get("tags", []):
            figure = root / "results" / "attribution.png"
            cell["outputs"].append({
                "output_type": "display_data",
                "data": {"image/png": base64.b64encode(figure.read_bytes()).decode("ascii")},
                "metadata": {},
            })
    notebook.setdefault("metadata", {})["execution"] = {
        "method": "in-process Python cell execution; no Jupyter kernel or socket",
        "executed_cells": execution_count,
    }
    notebook_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    result = {
        "status": "success",
        "method": "executed every notebook code cell in shared Python process",
        "cells_executed": execution_count,
        "outputs": "stdout and generated figure embedded in notebook",
        "kernel_note": "No Jupyter kernel startup was attempted by this runner; no kernel validation is claimed.",
    }
    (root / "results" / "notebook-execution.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    execute()
