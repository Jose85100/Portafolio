"""Execute notebook cells in-process (no kernel sockets or external services)."""

import base64
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import nbformat
from IPython.display import Image

path = Path(__file__).parent / "notebook.ipynb"
notebook = nbformat.read(path, as_version=4)
namespace = {"__name__": "__main__"}
displays: list[object] = []


def collect_display(obj: object) -> None:
    displays.append(obj)


namespace["display"] = collect_display
for index, cell in enumerate(notebook.cells, start=1):
    if cell.cell_type != "code":
        continue
    cell.outputs = []
    stdout = StringIO()
    with redirect_stdout(stdout):
        exec(compile(cell.source, f"notebook-cell-{index}", "exec"), namespace)  # noqa: S102
    output_text = stdout.getvalue()
    if output_text:
        cell.outputs.append(
            nbformat.v4.new_output("stream", name="stdout", text=output_text)
        )
    for obj in displays:
        if isinstance(obj, Image):
            data = obj.data
            if isinstance(data, str):
                data = data.encode()
            cell.outputs.append(
                nbformat.v4.new_output(
                    "display_data",
                    data={"image/png": base64.b64encode(data).decode()},
                    metadata={},
                )
            )
        elif hasattr(obj, "to_html"):
            cell.outputs.append(
                nbformat.v4.new_output(
                    "display_data",
                    data={"text/html": obj.to_html(), "text/plain": obj.to_string()},
                    metadata={},
                )
            )
        else:
            cell.outputs.append(
                nbformat.v4.new_output(
                    "display_data", data={"text/plain": str(obj)}, metadata={}
                )
            )
    displays.clear()
    cell.execution_count = index
nbformat.write(notebook, path)
