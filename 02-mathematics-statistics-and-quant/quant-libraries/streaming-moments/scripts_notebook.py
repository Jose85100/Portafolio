"""Execute29October streaming moments notebook in a fresh IPython namespace."""

from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}
nb.metadata.execution = {
    "executor": "IPython in-process",
    "scope": "fresh shell, sequential execution, abort on error; separate kernel not tested",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(
        "# Varianza fusionable y cancelación\nPregunta: ¿una traslación grande destruye la varianza computada? Se auditan algoritmos clásicos, sin novedad algorítmica. Hipótesis: el resumen desplazado conserva error absoluto <=1e-10 hasta offset1e12 para el fixture determinista. No se promete invariancia exacta en coma flotante."
    ),
    code(
        "import json,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\ns=json.loads(Path('results/summary.json').read_text())\nprint(json.dumps(s,indent=2))"
    ),
    md(
        "## Métodos\nM2 se actualiza con Welford sobre diferencias respecto al primer dato; Chan permite fusionar particiones. Decimal80 calcula el oráculo sobre los floats recibidos, no sobre números originales ya redondeados. ddof=0."
    ),
    code(
        "rows=list(csv.DictReader(Path('results/raw.csv').open()))\nprint([r for r in rows if r['n']=='4096' and r['offset']=='1000000000000.0'])"
    ),
    code("display(Image(filename='results/audit.png'))"),
    md(
        "## Resultado negativo y conclusión\nA1e16 los incrementos originales 0,1,2,3 no son todos representables. Ningún algoritmo recupera datos perdidos. NumPy dos pasadas es un baseline fuerte; no se afirma superioridad general. Tiempos de una llamada con tracemalloc son diagnósticos, no ranking de velocidad. Prototipo reproducible, sin validación operacional."
    ),
    code(
        "assert s['max_error_representable']['shifted_stream']<=1e-10\nassert s['max_error_representable']['shifted_merge127']<=1e-10\nprint('Hipótesis local verificada; error de representación:',s['representation_loss'])"
    ),
]
InteractiveShell.clear_instance()
shell = InteractiveShell.instance()
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.execution_count = count
    cell.outputs = []
    for name, value in [("stdout", captured.stdout), ("stderr", captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output("stream", name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(
            nbf.v4.new_output(
                "display_data", data=output.data, metadata=output.metadata
            )
        )
nbf.validate(nb)
nbf.write(nb, root / "notebook.ipynb")
