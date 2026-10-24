"""Create and execute a small sequential IPython notebook without socket kernels."""

import sys
from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(
        "# Calibración KYC contaminada: cota y coste\n## Resumen\nSe compara el rango ordinario con una envolvente que requiere cota externa válida del número de contaminantes. Las tasas se calculan abajo. Datos sintéticos; no estima fraude real."
    ),
    nbf.v4.new_markdown_cell(
        "## Método y supuestos\nScore fijo, referencia con c contaminantes, c≤m<n, y n−c scores limpios intercambiables con el próximo inlier. El subconjunto limpio no se elige por sus propios scores.\n\nCon k scores observados ≥s, usamos $p_m(s)=\\min(1,(1+k)/(n-m+1))$. Sea k0 el conteo limpio: k≥k0 y n−m≤n−c, por lo que p_m domina el p limpio. La inclusión {p_m≤α}⊆{p_limpio≤α} transmite validez marginal. No se garantiza FPR de una calibración fijada, validez individual ni FDR de lote. La cota m no se estima aquí."
    ),
    nbf.v4.new_code_cell(
        "import csv, json\nfrom pathlib import Path\nfrom IPython.display import display, Image\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nprint(json.dumps(metrics,indent=2))"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos y resultados\n80 semillas; n=499, c=199 en escenarios contaminados. Mismos scores de prueba en ambos métodos y escenarios. Barras de error son ±1,96 SE de la media entre semillas independientes; no intervalos individuales ni por cliente."
    ),
    nbf.v4.new_code_cell(
        "rows=list(csv.DictReader((root/'results/summary.csv').open()))\nfor row in rows: print(row)\ndisplay(Image(filename=str(root/'results/audit.png')))"
    ),
    nbf.v4.new_markdown_cell(
        "## Falsación y comprobaciones\nUna cota subestimada m=99 frente a c=199 rompe el supuesto. Contaminación de scores altos conserva tipo I a costa de potencia nula. En limpio, una cota excesiva es conservadora y pierde potencia."
    ),
    nbf.v4.new_code_cell(
        "from src.guard import ContaminationGuard\nassert metrics['hypothesis_passed']\nassert ContaminationGuard([1.,2.,2.,3.],1).p_value(4.)==.25\nassert ContaminationGuard([1.,2.,2.,3.]).p_value(2.)==.8\nfor row in csv.DictReader((root/'results/performance.csv').open()): print(row)\nprint('Checks passed')"
    ),
    nbf.v4.new_markdown_cell(
        "## Conclusión y límites\nLa corrección reduce falsas alertas bajo la cota correcta, pero no descubre cuántos contaminantes hay. Solo justifica un piloto de auditoría con referencias adjudicadas, no rechazo automático. No es un algoritmo nuevo de la literatura ni un sistema operativo. Véase informe.md y cinco fuentes verificadas en referencias.bib."
    ),
]
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.metadata["execution"] = {
    "mode": "IPython sequential in-process",
    "reason": "real cells executed; no ZeroMQ socket kernel required",
}
shell = InteractiveShell.instance()
for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), 1):
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.execution_count = count
    cell.outputs = []
    if captured.stdout:
        cell.outputs.append(
            nbf.v4.new_output("stream", name="stdout", text=captured.stdout)
        )
    if captured.stderr:
        cell.outputs.append(
            nbf.v4.new_output("stream", name="stderr", text=captured.stderr)
        )
    for rich in captured.outputs:
        cell.outputs.append(
            nbf.v4.new_output("display_data", data=rich.data, metadata=rich.metadata)
        )
nbf.validate(nb)
nbf.write(nb, root / "notebook.ipynb")
