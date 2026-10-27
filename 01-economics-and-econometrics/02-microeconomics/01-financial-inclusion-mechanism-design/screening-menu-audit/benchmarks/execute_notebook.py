"""Execute notebook sequentially in a clean in-process IPython shell.

No Jupyter kernel is launched: sandbox may forbid its sockets. Preserves
execution count, stdout and rich display data. Any execution error aborts.
"""

from pathlib import Path
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
nb = nbformat.read(root / "notebook.ipynb", as_version=4)
shell = InteractiveShell.instance(user_ns={})
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f"Notebook cell {count} failed") from (
            result.error_before_exec or result.error_in_exec
        )
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
    cell.execution_count = count
nb.metadata["execution_method"] = (
    "Sequential clean in-process IPython; no Jupyter kernel/socket. All code cells executed; error aborts."
)
nbformat.validate(nb)
nbformat.write(nb, root / "notebook.ipynb")
print(f"Executed {count} code cells in process.")
