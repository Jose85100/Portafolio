"""Actual notebook-cell execution, without network kernel sockets."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook(cells=[
    nbf.v4.new_markdown_cell('# Polyhedral Freeze Audit — S2\nPregunta: ¿un soporte singular factible implica familia positiva? Mismo juego u_i=a_i(theta+alpha*a_j-c), dos tipos por prestamista. Cada patrón define producto de dos poliedros bidimensionales. Vértices y dimensión se calculan con Fraction; no con el rango de ecuaciones redundantes.'),
    nbf.v4.new_code_cell("import csv,json\nfrom pathlib import Path\nfor row in csv.DictReader(Path('results/summary.csv').open()): print(row)\nprint(json.loads(Path('results/metadata.json').read_text()))"),
    nbf.v4.new_markdown_cell('En el caso q=.5,c=.9,alpha=.8: cada prestamista puede elegir cualquier punto del segmento x(0)+x(1)=1. Su producto tiene dimensión 2; también existen dos puntos aislados. La familia no equivale a una distribución de selección ni a mecanismos observables distintos.'),
    nbf.v4.new_code_cell("from IPython.display import Image,display\ndisplay(Image(filename='results/family.png'))"),
    nbf.v4.new_code_cell("print(Path('results/coverage.txt').read_text())\nprint(Path('results/lp_oracle.csv').read_text()[:2500])")])
nb.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
nb.metadata.execution_method = 'IPython in-process, actual cells and captured outputs'
os.chdir(root); shell = InteractiveShell.instance(); count = 0
for cell in nb.cells:
    if cell.cell_type != 'code': continue
    count += 1
    with capture_output() as captured: result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec: raise RuntimeError('Notebook failed')
    cell.execution_count = count; cell.outputs = []
    for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
        if value: cell.outputs.append(nbf.v4.new_output('stream', name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
nbf.write(nb, root/'notebook.ipynb')
