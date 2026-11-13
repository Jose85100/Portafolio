"""Execute the prior-sensitivity notebook in-process when a Jupyter kernel is unavailable."""
import base64
import os
from pathlib import Path
import nbformat as nb
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

path = Path(__file__).resolve().parents[1] / 'notebooks' / 'prior_sensitivity.ipynb'
notebook = nb.read(path, as_version=4)
os.chdir(path.parent)
shell = InteractiveShell.instance()
count = 0
for cell in notebook.cells:
    if cell.cell_type != 'code':
        continue
    count += 1
    with capture_output() as output:
        result = shell.run_cell(cell.source)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(result.error_before_exec or result.error_in_exec)
    cell.execution_count = count
    cell.outputs = []
    if output.stdout:
        cell.outputs.append(nb.v4.new_output('stream', name='stdout', text=output.stdout))
    if output.stderr:
        cell.outputs.append(nb.v4.new_output('stream', name='stderr', text=output.stderr))
    if count == 2:
        png = (path.parent.parent / 'results' / 'prior_sensitivity.png').read_bytes()
        cell.outputs.append(nb.v4.new_output('display_data', data={'image/png': base64.b64encode(png).decode(), 'text/plain': 'EVSI por concentración del prior'}, metadata={}))
nb.write(notebook, path)
print(f'executed {count} code cells via IPython in-process')
