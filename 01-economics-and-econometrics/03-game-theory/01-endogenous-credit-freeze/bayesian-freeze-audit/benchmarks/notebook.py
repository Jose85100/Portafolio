from pathlib import Path
import nbformat as nbf
import os
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
root=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook(cells=[
 nbf.v4.new_markdown_cell("# Juego bayesiano de congelación de crédito — S2\nJuego finito calibrado, no evidencia empírica ni inferencia causal. Pregunta: ¿un solo punto fijo oculta multiplicidad? Modelo: u_i=a_i(theta+alpha*a_j-c), dos señales privadas condicionalmente independientes. H1: al menos dos BNE y amplitud de freeze mayor a .5 en la configuración principal. Véase informe.md para supuestos, literatura y límites."),
 nbf.v4.new_code_cell("import csv, json\nfrom pathlib import Path\nrows=list(csv.DictReader(Path('results/main.csv').open()))\nfor row in rows: print(row)\nprint(json.loads(Path('results/metadata.json').read_text()))"),
 nbf.v4.new_markdown_cell("Enumeración de los 16 perfiles puros. Los límites entre equilibrios no constituyen probabilidades de selección."),
 nbf.v4.new_code_cell("from IPython.display import Image, display\ndisplay(Image(filename='results/equilibria.png'))"),
 nbf.v4.new_code_cell("print(Path('results/coverage.txt').read_text())")])
nb.metadata.kernelspec={"display_name":"Python 3","language":"python","name":"python3"}
# Execute actual cells in-process: avoids network sockets required by a Jupyter kernel.
os.chdir(root)
shell = InteractiveShell.instance()
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError("Notebook execution failed")
    cell.execution_count = count
    cell.outputs = []
    if captured.stdout:
        cell.outputs.append(nbf.v4.new_output("stream", name="stdout", text=captured.stdout))
    if captured.stderr:
        cell.outputs.append(nbf.v4.new_output("stream", name="stderr", text=captured.stderr))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output("display_data", data=output.data, metadata=output.metadata))
nb.metadata["execution_method"] = "IPython in-process; actual cells executed, no socket kernel"
nbf.write(nb,root/'notebook.ipynb')
