"""Build a small notebook and execute all code cells with real IPython capture."""

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
        "# Liquidez: incertidumbre de transición y reserva\n## Resumen\nMVP pequeño: matriz nominal versus intervalos hipotéticos porfila. Una banda rectangular permite adaptar transición por tiempo/caja/régimen. NO es intervalo de confianza ni supremo definido sobre una única matriz fija. Datos sintéticos; resultados calculados abajo."
    ),
    nbf.v4.new_markdown_cell(
        "## Método y supuestos\nFlujos(+1,−2),inicial(.8,.2),qnominal=(.05,.8). Intervalosq0=[.03,.07],q1=[.7,.9]. No todas las matrices conservan marginales estacionarios del ciclo27.\n\nTras el flujo,c'=c+g(s). Si c'<0 se absorbe riesgo1; si no quedan flujos,riesgo0. $U_h(c,s)=\\max_{q\\in[lo_s,hi_s]}[(1-q)U_{h-1}(c',0)+qU_{h-1}(c',1)]$. Es afín enq, así basta los extremos. La banda inferior usa min con continuacionesinferiores. Naturaleza elige de forma rectangular en cada estado/fecha, no una sola matriz para toda la trayectoria."
    ),
    nbf.v4.new_markdown_cell(
        "### Pregunta falsable\n¿La cota supera nominal al menos5pp en caja6,H20?¿La reserva robusta supera nominal≥3unidades para objetivo5%? Umbrales enconfig. La búsqueda0..30 se agotó; se extendió a0..40 porque20salidas de−2 acotan pérdida máxima. No se cambió hipótesis."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport json,csv\nfrom IPython.display import display,Image\nfrom src.model import risk_band\nfrom src.baseline import nominal\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nprint(json.dumps(metrics,indent=2))\nassert metrics['hypothesis_passed']"
    ),
    nbf.v4.new_markdown_cell(
        "## Resultados\n41reservas y cuatro esquinas estáticas por reserva, sin simulaciónaleatoria. El baseline nominal usa el forwardDP27 sin modificar; checksum enJSON. La banda proviene del modelo supuesto, no de datos estimados. Reserva34 no es recomendación para un banco real."
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/audit.png')))\nrows=list(csv.DictReader((root/'results/curves.csv').open()))\nfor row in rows:\n if int(row['cash']) in [6,22,33,34,40]: print(row)"
    ),
    nbf.v4.new_markdown_cell(
        "## Oráculo y falsaciones\nDesde caja0/régimennormal: primer flujo+1,día2estrés−2 cruza frontera; riesgo exacto=q0. H1 no depende de transición y singleton reproduce nominal. En este escenario el adversario adaptativo NO empeora una esquina fija observada: no se finge superioridad del método máscomplejo."
    ),
    nbf.v4.new_code_cell(
        "band=risk_band(0,2,[[.1,.4],[.2,.8]],[1,0])\nassert band.lower==.1 and band.upper==.4\nassert risk_band(1,1,[[0,1],[0,1]]).lower==risk_band(1,1,[[0,1],[0,1]]).upper\np=nominal(6,20,[.05,.8])\nb=risk_band(6,20,[[.05,.05],[.8,.8]])\nassert abs(b.lower-p)<1e-12 and abs(b.upper-p)<1e-12\nprint('Analytic/singleton checks passed')\nprint('Máximo gap adaptativo/esquina observado:',metrics['maximum_adaptive_static_gap'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Límites y siguiente iteración\nRectangularidad fuerte y rangos hipotéticos; no cobertura estadística, no equivalencia universal con matrizfija, no aprendizaje ni fondeo operativo. Añadir región de confianza temporal sería una tarea distinta. Cinco fuentes primarias e informe14p detallan supuestos y lectura. Prototipo de componente; no operación."
    ),
]
nb.metadata["kernelspec"] = {
    "display_name": "Python3",
    "language": "python",
    "name": "python3",
}
nb.metadata["execution"] = {
    "mode": "IPython sequential in-process",
    "outputs": "captured from real execution",
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
