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
nb.cells.extend(
    [
        nbformat.v4.new_markdown_cell(
            "## Contrato consumidor — 2026-10-16\n\n"
            "Hipótesis: conservar el racional al decidir ES > 0 evita que un float cero "
            "oculte una contribución positiva. Se reutilizan los 388 inputs originales y el "
            "oráculo hinge independiente. No se afirma corrección universal cerca de otros umbrales. "
            "Un rechazo no es una decisión de seguridad."
        ),
        nbformat.v4.new_code_cell(
            "from src.consumer import decide, encode\n"
            "p=decide([0.0,5e-324], '0', .5, [3.0,1.0])\n"
            "keys=['status','breach','es_float','output_rounds_to_zero','comparison_basis']\n"
            "print({k:p[k] for k in keys})\n"
            "assert p['es_float']==0 and p['breach'] is True\n"
            "assert json.loads(encode(p)) == p\n"
            "reject=decide([1e308,0], '0', weights=[1e-300,1e300], policy='raise')\n"
            "print('Rechazo:', reject['status'], reject['breach'])\n"
            "assert reject['breach'] is None"
        ),
        nbformat.v4.new_code_cell(
            "from IPython.display import HTML\n"
            "s=json.loads(Path('results/consumer-summary.json').read_text())\n"
            "display(HTML('<table><tr><th>388 casos, umbral cero</th><th>Errores de decisión</th></tr>'"
            "+f'<tr><td>Consumidor float del guard</td><td>{s[\"naive_errors\"]}</td></tr>'"
            "+f'<tr><td>Contrato racional</td><td>{s[\"contract_errors\"]}</td></tr></table>'))\n"
            "assert s['contract_errors']==0\n"
            "print('Limitación: esta prueba de signo no certifica decisiones próximas a todo umbral.')"
        ),
    ]
)
nb.cells.extend(
    [
        nbformat.v4.new_markdown_cell(
            "## Recepción validada — 2026-10-17\n\n"
            "Goal: validar consistencia interna antes de consumir ES/decisión; no autenticar "
            "al emisor. Setup: paquetes v1 generados desde las mismas fixtures, "
            "mutaciones deterministas y límites 32768 bytes/2048 caracteres por entero. "
            "Se compara el parser json.loads con la recepción validada."
        ),
        nbformat.v4.new_code_cell(
            "from src.packet import decode, PacketError\n"
            "good=decide([0.0,5e-324], '0', .5, [3.,1.])\n"
            "assert decode(encode(good).encode()) == good\n"
            "bad=dict(good, breach=False)\n"
            "try:\n    decode(encode(bad).encode())\n"
            "except PacketError as error:\n    print('Rechazo coherencia:',error)\n"
            "else:\n    raise AssertionError('Mutation accepted')\n"
            "print('Paquete original positivo aceptado:',good['breach'])"
        ),
        nbformat.v4.new_code_cell(
            "v=json.loads(Path('results/packet-summary.json').read_text())\n"
            "print({k:v[k] for k in ['valid_packets','invalid_mutants',"
            "'json_invalid_accepted','validator_invalid_accepted','validator_valid_rejected']})\n"
            "assert v['validator_invalid_accepted']==0 and v['validator_valid_rejected']==0\n"
            "negative=json.loads(Path('results/packet-negative-control.json').read_text())\n"
            "assert decode(encode(negative['forged_packet']).encode()) == negative['forged_packet']\n"
            "print('Control negativo: falsificación coherente aceptada; no hay autenticación.')"
        ),
        nbformat.v4.new_markdown_cell(
            "### Next steps y límites\n\n"
            "El corpus de mutaciones no es una tasa de ataques reales. El validador rechaza "
            "inconsistencias pero no demuestra ES verdadero, origen ni frescura; hace falta "
            "recalcular o verificar procedencia. Ver informe-recepcion.md."
        ),
    ]
)
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
print("Seven code cells executed with real output; notebook validated")
