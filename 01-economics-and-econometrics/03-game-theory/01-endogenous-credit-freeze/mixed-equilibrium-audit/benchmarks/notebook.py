"""Execute actual narrative notebook cells in IPython without socket kernels."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook(cells=[
    nbf.v4.new_markdown_cell('# Mixed Freeze Audit — S2\nPregunta: ¿excluir estrategias mixtas altera el conjunto de resultados? Mismo juego de dos prestamistas: u_i=a_i(theta+alpha*a_j-c). Enumeramos 81 soportes. Los casos degenerados se rechazan; no afirmamos listar un continuo de equilibrios.'),
    nbf.v4.new_code_cell("import csv, json\nfrom pathlib import Path\nfor row in csv.DictReader(Path('results/equilibria.csv').open()): print(row)\nprint(json.loads(Path('results/summary.json').read_text()))"),
    nbf.v4.new_markdown_cell('Hipótesis principal: aparecen al menos dos equilibrios adicionales. Contraste negativo: no se presupone que los límites extremos de congelación aumenten. No hay datos empíricos ni probabilidades de selección estimadas.'),
    nbf.v4.new_code_cell("from IPython.display import Image, display\ndisplay(Image(filename='results/comparison.png'))"),
    nbf.v4.new_code_cell("print(Path('results/coverage.txt').read_text())\nprint(Path('results/negative.csv').read_text())")])
nb.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
nb.metadata.execution_method = 'IPython in-process: actual cells and captured outputs'
os.chdir(root); shell = InteractiveShell.instance(); count = 0
for cell in nb.cells:
    if cell.cell_type != 'code':
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError('Notebook execution failed')
    cell.execution_count = count; cell.outputs = []
    for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output('stream', name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
nbf.write(nb, root/'notebook.ipynb')
