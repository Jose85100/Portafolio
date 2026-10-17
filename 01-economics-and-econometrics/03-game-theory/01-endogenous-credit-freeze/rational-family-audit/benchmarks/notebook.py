"""Execute actual narrative notebook cells with captured outputs, no kernel sockets."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook(cells=[
    nbf.v4.new_markdown_cell('# Rational Family Audit\n## tl;dr\nEste notebook muestra las comparaciones exactas ejecutadas con Gambit racional y el baseline poliédrico. La comparación es entre productos de envolventes convexas compatibles; no se convexifica la unión completa de equilibrios.'),
    nbf.v4.new_markdown_cell('## Context & Methods\nGambit16.4.1 lee el NFG real y enumera extremos racionales. El código nuevo proyecta marginales por tipo, construye el grafo de compatibilidad usando payoffs directos y enumera bicliques máximos.\n### Key Assumptions\nDos prestamistas y dos tipos; señales condicionalmente independientes; prior interior; payoff a_i(theta+alpha*a_j-c). La reconstrucción depende de la enumeración externa completa. Sin inferencia causal ni datos observados; S2 parcial.'),
    nbf.v4.new_code_cell("import csv,json\nfrom pathlib import Path\nprint(json.loads(Path('results/config.json').read_text()))\nprint(json.loads(Path('results/metadata.json').read_text()))"),
    nbf.v4.new_markdown_cell('## Data\nMatrices sintéticas racionales .nfg; el parser externo verifica las32 entradas. Perfiles crudos y familias exactas están en profiles.csv y families.json. Seed20261017.'),
    nbf.v4.new_code_cell("print(Path('results/regular.nfg').read_text())\nfor row in list(csv.DictReader(Path('results/summary.csv').open()))[:5]:\n    print({k:row[k] for k in ['scenario','gambit_profiles','baseline_families','reconstructed_families','dimensions','exact_equal','max_interim_regret']})"),
    nbf.v4.new_markdown_cell('## Results\nFigura editable desde benchmarks/run.py, generada a partir de resultados ejecutados. Las barras derechas son controles negativos, no estimaciones empíricas.'),
    nbf.v4.new_code_cell("from IPython.display import Image,display\ndisplay(Image(filename='results/comparison.png'))"),
    nbf.v4.new_code_cell("print(Path('results/ablations.csv').read_text())\nprint(Path('results/coverage.txt').read_text())"),
    nbf.v4.new_markdown_cell('## Takeaways\nLa igualdad exacta de familias en los casos ejecutados amplía la evidencia S2, no demuestra un teorema de completitud general ni S3 del programa. Un punto o una envolvente global pierden la estructura de multiplicidad; ver informe.md para casos negativos, coste y límites.')])
nb.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
nb.metadata.execution_method = 'Actual IPython in-process execution'
os.chdir(root)
shell = InteractiveShell.instance()
count = 0
for cell in nb.cells:
    if cell.cell_type != 'code':
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError('Notebook cell execution failed')
    cell.execution_count = count
    cell.outputs = []
    for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output('stream', name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
nbf.validate(nb)
nbf.write(nb, root/'notebook.ipynb')
