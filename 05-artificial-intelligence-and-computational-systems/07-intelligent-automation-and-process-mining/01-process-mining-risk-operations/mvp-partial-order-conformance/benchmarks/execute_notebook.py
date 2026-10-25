"""Execute real cells sequentially in-process; no Jupyter socket required.

Captures IPython display/stream outputs, validates and saves nbformat.
This is not a separate Jupyter-kernel validation.
"""

import sys
from pathlib import Path

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

p = Path("notebook.ipynb").resolve()
sys.path.insert(0, str(p.parent))
nb = nbformat.read(p, as_version=4)
shell = InteractiveShell.instance()
shell.user_ns.clear()
shell.init_user_ns()
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        sys.stderr.write(captured.stdout + captured.stderr)
        raise RuntimeError(f"Notebook cell {count} failed") from (
            result.error_before_exec or result.error_in_exec
        )
    cell.execution_count = count
    outputs = []
    if captured.stdout:
        outputs.append(
            nbformat.v4.new_output("stream", name="stdout", text=captured.stdout)
        )
    if captured.stderr:
        outputs.append(
            nbformat.v4.new_output("stream", name="stderr", text=captured.stderr)
        )
    for output in captured.outputs:
        outputs.append(
            nbformat.v4.new_output(
                "display_data", data=output.data, metadata=output.metadata
            )
        )
    cell.outputs = outputs
nb.metadata["execution_method"] = (
    "IPython in-process sequential cells; Jupyter kernel sockets unavailable in managed environment"
)
nbformat.validate(nb)
nbformat.write(nb, p)
print(f"Executed and saved {count} code cells via IPython in-process")
