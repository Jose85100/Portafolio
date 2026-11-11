"""Execute notebook code cells in order using only the Python standard library."""
import contextlib
import io
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.chdir(root)
path = root / "notebook.ipynb"
nb = json.loads(path.read_text())
namespace = {"__name__": "__main__"}
for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue
    source = "".join(cell["source"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(source, "notebook-cell", "exec"), namespace)  # noqa: S102 - executes the checked-in notebook cells
    rendered = out.getvalue()
    cell["outputs"] = ([{"output_type": "stream", "name": "stdout", "text": rendered.splitlines(True)}]
                       if rendered else [])
    cell["execution_count"] = nb["cells"].index(cell)+1
nb["metadata"]["execution"] = "executed in-process via scripts/execute_notebook.py"
path.write_text(json.dumps(nb, ensure_ascii=False, indent=1)+"\n")
print("Executed all notebook code cells; outputs stored in notebook.ipynb")
