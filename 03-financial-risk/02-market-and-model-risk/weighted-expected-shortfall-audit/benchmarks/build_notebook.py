"""Execute notebook cells in-process with real IPython output capture (no sockets)."""

import contextlib
import io
import sys
from pathlib import Path
from typing import Any

import nbformat
from IPython.core.interactiveshell import InteractiveShell

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
nb = nbformat.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Weighted ES", "language": "python", "name": "weighted-es"}
nb.cells = [
    nbformat.v4.new_markdown_cell(
        "# Auditoría de ES ponderado\n\n"
        "Pregunta: ¿las convenciones de cola calculan la misma medida sobre pérdidas discretas? "
        "Hipótesis: la integración de masa fraccionaria coincide con el LP a tolerancia 1e-8. "
        "La fórmula es conocida (Acerbi–Tasche; Rockafellar–Uryasev), no un estimador nuevo.\n\n"
        "Convención: pérdidas positivas, confianza 0.975, escenarios finitos; pesos conocidos. "
        "Resultados numéricos, no backtesting fuera de muestra."
    ),
    nbformat.v4.new_code_cell(
        "import sys, json, csv\nfrom pathlib import Path\n"
        "from src.tail import weighted_tail\nfrom src.oracle import lp_es\n"
        "print('Python:', sys.version.split()[0])\n"
        "x = [0.] * 99 + [100.]\nprint('ES exacto:', weighted_tail(x).es)\n"
        "print('LP:', lp_es(x))\nprint('Escenarios ponderados:', weighted_tail([0,100], weights=[99,1]))"
    ),
    nbformat.v4.new_markdown_cell(
        "## Comparación justa\n\n"
        "Se ejecutan los cuerpos de funciones del commit auditado, sin sus demos. "
        "El baseline de liquidez ya es correcto para probabilidades iguales. "
        "Los baselines uniformes en la distribución ponderada son una ablación de pesos, "
        "no un competidor con soporte ponderado."
    ),
    nbformat.v4.new_code_cell(
        "rows = list(csv.DictReader(Path('results/summary.csv').open()))\n"
        "for r in rows:\n    print(r['distribution'], r['method'], 'MAE=', "
        "r['mean_abs_error'], 'invalid=', r['invalid'])\n"
        "meta=json.loads(Path('results/metadata.json').read_text())\n"
        "print('Max error vs LP:', meta['max_oracle_abs_error'])\n"
        "assert meta['max_oracle_abs_error'] < 1e-8"
    ),
    nbformat.v4.new_code_cell(
        "from IPython.display import Image, display\ndisplay(Image(filename='results/audit.png'))"
    ),
    nbformat.v4.new_markdown_cell(
        "## Conclusiones y límites\n\n"
        "La diferencia es definicional, no una mejora probada del pronóstico. "
        "El método exacto consume más recursos que el promedio por umbral. "
        "No estima probabilidades ni incertidumbre de población; no representa capital regulatorio. "
        "La cola estricta puede estar vacía. Ver informe.md y referencias.bib. "
        "Siguiente paso: migración con pruebas de regresión y contrato común Python/C++."
    ),
]
shell = InteractiveShell.instance()
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    outputs: list[Any] = []
    stdout, stderr = io.StringIO(), io.StringIO()

    def capture(data: dict[str, Any], metadata: dict[str, Any] | None = None, **kwargs: Any) -> None:
        outputs.append(nbformat.v4.new_output("display_data", data=data, metadata=metadata or {}))

    original_publish = shell.display_pub.publish
    setattr(shell.display_pub, "publish", capture)
    try:
        cell.execution_count = shell.execution_count
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            execution = shell.run_cell(cell.source, store_history=True, silent=False)
        if execution.error_before_exec or execution.error_in_exec:
            raise RuntimeError(f"Notebook execution failed: {stderr.getvalue()} {stdout.getvalue()}")
    finally:
        setattr(shell.display_pub, "publish", original_publish)
    if stdout.getvalue():
        outputs.insert(0, nbformat.v4.new_output("stream", name="stdout", text=stdout.getvalue()))
    if stderr.getvalue():
        outputs.append(nbformat.v4.new_output("stream", name="stderr", text=stderr.getvalue()))
    cell.outputs = outputs
nbformat.validate(nb)
nbformat.write(nb, root / "notebook.ipynb")
assert all(c.execution_count is not None and c.outputs for c in nb.cells if c.cell_type == "code")
print("Executed notebook: three code cells, real IPython outputs; no Jupyter sockets required")
