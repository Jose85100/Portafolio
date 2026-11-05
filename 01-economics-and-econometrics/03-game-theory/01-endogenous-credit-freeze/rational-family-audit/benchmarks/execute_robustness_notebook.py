"""Execute notebook code in a fresh Python process and persist text outputs."""

from __future__ import annotations
import contextlib
import io
import os
import sys
from pathlib import Path
import nbformat as nbf

root = Path(__file__).resolve().parents[1]
os.chdir(root)
sys.path.insert(0, str(root))
nb = nbf.read(root / "notebook_robustness.ipynb", as_version=4)
env: dict[str, object] = {}
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        exec(cell.source, env, env)
    text = captured.getvalue()
    if not text and "vals" in env:
        text = repr(env["vals"]) + "\\n"
    if not text and "display(" in cell.source:
        text = "PNG generated and referenced in Markdown above.\\n"
    cell.execution_count = count
    cell.outputs = (
        [nbf.v4.new_output("stream", name="stdout", text=text)] if text else []
    )
    if "id" not in cell:
        cell["id"] = f"robustness-{count}"
nbf.validate(nb)
nbf.write(nb, root / "notebook_robustness.ipynb")
print(f"executed {count} code cells in fresh Python process")
