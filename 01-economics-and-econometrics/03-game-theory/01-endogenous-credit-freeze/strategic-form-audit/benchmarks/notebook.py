"""Execute and save actual IPython cells without opening kernel network sockets."""
import os
from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook(cells=[
    nbf.v4.new_markdown_cell('# Strategic Form Audit\n## tl;dr\nEl contraste externo recupera 5/5 puntos regulares. La enumeración de vértices externa falla en indiferencia total; no se confunde fallo con ausencia de equilibrio. Una tolerancia ex ante puede ocultar una desviación interina grande.'),
    nbf.v4.new_markdown_cell('## Context & Methods\nDos prestamistas, estado y señales binarias, u_i=a_i(theta+alpha*a_j-c). Forma estratégica ex ante 4x4 calculada por suma de ocho estados. Nashpy 0.0.43 es externo; el poliedro racional existente es baseline.\n### Key Assumptions\nSeñales condicionalmente independientes, prior interior, aleatorización independiente entre jugadores, sin datos reales ni identificación. La proyección conserva marginales por tipo, no correlaciones entre acciones contrafactuales.'),
    nbf.v4.new_code_cell("import csv,json\nfrom pathlib import Path\nprint(json.loads(Path('results/config.json').read_text())['regular'])\nprint(json.loads(Path('results/metadata.json').read_text()))"),
    nbf.v4.new_markdown_cell('## Data\nPayoffs sintéticos racionales exportados a .nfg. Orden de políticas: (0,0),(0,1),(1,0),(1,1); jugador uno varía más rápido. No se ejecutó Gambit; round-trip usa un parser limitado propio y Nashpy consume sus matrices.'),
    nbf.v4.new_code_cell("print(Path('results/regular.nfg').read_text())"),
    nbf.v4.new_markdown_cell('## Results\nLa tabla cuenta vértices del baseline encontrados a tolerancia 1e-8; una lista finita no representa una familia continua completa.'),
    nbf.v4.new_code_cell("for row in list(csv.DictReader(Path('results/summary.csv').open()))[:8]:\n    print({k:row[k] for k in ['scenario','method','target_vertices','matched_vertices','max_interim_regret','status']})"),
    nbf.v4.new_code_cell("from IPython.display import Image,display\ndisplay(Image(filename='results/comparison.png'))"),
    nbf.v4.new_code_cell("print(Path('results/rare_type_ablation.csv').read_text())\nprint(Path('results/coverage.txt').read_text())"),
    nbf.v4.new_markdown_cell('## Takeaways\nValidar regret condicional por tipo y conservar familias poliédricas: menor regret ex ante no certifica por sí solo un equilibrio interino aproximado uniforme. Cobertura medida sólo de src/ nuevo; pruebas no equivalen a demostración de completitud. Ver informe.md y referencias.bib para límites y literatura.')])
nb.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
nb.metadata.execution_method = 'Actual IPython in-process execution, captured outputs'
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
        raise RuntimeError('Notebook execution failed')
    cell.execution_count = count
    cell.outputs = []
    for name, value in [('stdout', captured.stdout), ('stderr', captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output('stream', name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbf.v4.new_output('display_data', data=output.data, metadata=output.metadata))
nbf.validate(nb)
nbf.write(nb, root/'notebook.ipynb')
