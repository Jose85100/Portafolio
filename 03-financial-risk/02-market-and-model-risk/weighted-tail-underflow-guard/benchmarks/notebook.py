"""Execute authored notebook cells with real IPython output capture; no sockets."""

import contextlib
import io
import sys
from pathlib import Path
from typing import Any

import nbformat
from IPython.core.interactiveshell import InteractiveShell

project = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project))
nb = nbformat.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["execution_method"] = "IPython in-process; real stream/display_data capture"
nb.cells = [
    nbformat.v4.new_markdown_cell(
        "# Guardar el ES contra underflow silencioso\n\n"
        "Pregunta: ¿se puede detectar una pérdida numérica y recalcular desde los inputs originales? "
        "Hipótesis: los fallbacks coinciden con el oráculo racional "
        "y el camino ordinario conserva el baseline. "
        "Los métodos son conocidos; el aporte es el guard, sus políticas y el benchmark del repo. "
        "Pérdidas positivas, pesos conocidos y valores interpretados en binary64."
    ),
    nbformat.v4.new_code_cell(
        "from src.guard import guarded_tail, TailUnderflowError\nfrom src.sources import legacy\n"
        "x, p = [1e308, 0.0], [1e-300, 1e300]\n"
        "print('Baseline:', legacy.weighted_tail(x, .975, p).es)\n"
        "r = guarded_tail(x, .975, p)\nprint('Protegido:', r.es, r.backend, r.fallback_reason)\n"
        "assert r.es > 0\n"
        "try:\n    guarded_tail(x, .975, p, policy='raise')\n"
        "except TailUnderflowError as error:\n    print('Rechazo explícito:', error)"
    ),
    nbformat.v4.new_markdown_cell(
        "## Experimento ejecutado\n\n"
        "Se reutilizan 207 fixtures del aporte C++ y se añade un barrido de exponentes. "
        "El baseline real queda sin modificar. La referencia hinge usa Fraction "
        "sobre inputs binarios exactos; "
        "el fallback integra masa de cola en racionales. No son dos copias del mismo algoritmo."
    ),
    nbformat.v4.new_code_cell(
        "import json, csv\nfrom pathlib import Path\n"
        "m=json.loads(Path('results/metadata.json').read_text())\nprint(m['summary'])\n"
        "assert m['summary']['guard_lost_representable'] == 0\n"
        "rows=list(csv.DictReader(Path('results/accuracy.csv').open()))\n"
        "for row in rows:\n    if row['reference_rounds_to_zero'] == 'True':\n"
        "        print('Resultado no representable:', row['id'], row['output_rounds_to_zero'])"
    ),
    nbformat.v4.new_code_cell(
        "from IPython.display import SVG, display\ndisplay(SVG(filename='results/comparison.svg'))"
    ),
    nbformat.v4.new_markdown_cell(
        "## Conclusión crítica\n\n"
        "La exactitud del fallback tiene costo: siempre-exacto es la ablación de velocidad. "
        "El guard no promete detectar todo error de redondeo. El presupuesto limita el fallback "
        "a 4096 filas; casos mayores se rechazan. Un ES racional no nulo puede redondear a cero "
        "al devolver float: se declara con un flag y se conserva "
        "la fracción. Sin inferencia sobre pronóstico, materialidad económica ni capital regulatorio. "
        "Ver informe.md y referencias.bib."
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

    original = shell.display_pub.publish
    setattr(shell.display_pub, "publish", capture)
    try:
        cell.execution_count = shell.execution_count
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            execution = shell.run_cell(cell.source, store_history=True)
        if execution.error_before_exec or execution.error_in_exec:
            raise RuntimeError(stdout.getvalue() + stderr.getvalue())
    finally:
        setattr(shell.display_pub, "publish", original)
    if stdout.getvalue():
        outputs.insert(0, nbformat.v4.new_output("stream", name="stdout", text=stdout.getvalue()))
    if stderr.getvalue():
        outputs.append(nbformat.v4.new_output("stream", name="stderr", text=stderr.getvalue()))
    cell.outputs = outputs
nbformat.validate(nb)
assert all(c.outputs and c.execution_count is not None for c in nb.cells if c.cell_type == "code")
nbformat.write(nb, project / "notebook.ipynb")
print("Three code cells executed with real output; notebook validated")
