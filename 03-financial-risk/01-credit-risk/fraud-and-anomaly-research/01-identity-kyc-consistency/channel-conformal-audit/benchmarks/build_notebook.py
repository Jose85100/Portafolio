from pathlib import Path
import sys
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(
        "# Auditoría de alertas KYC por canal\n## Resumen\nExperimento sintético: calibración agrupada frente a pooled; resultados calculados abajo. No es detector de fraude validado."
    ),
    nbf.v4.new_markdown_cell(
        "## Contexto y método\nScore fijo s=|residuo|, sin entrenamiento sobre calibración. Canales definidos antes de observar datos.\n\n$p_g(s)=(1+\\sum_i\\mathbf{1}[S_{gi}\\ge s])/(n_g+1)$. Alertar si $p_g\\le0.05$. Empates con >= son conservadores.\n\nBajo intercambiabilidad de inliers dentro del canal, el rango proporciona validez marginal en calibración y nuevo caso, no una garantía condicional en la muestra fijada. No controlamos FDR de un lote ni garantizamos igualdad entre personas. "
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport json, csv\nfrom IPython.display import display, Image\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nprint(json.dumps(metrics,indent=2))"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos y resultados\n60 semillas; canales con escalas 1 y 4. Normalidad es una elección del experimento, no requisito del rango. Drift cambia solo la dispersión de inliers en evaluación. Sparse reduce calibración a 9 por canal."
    ),
    nbf.v4.new_code_cell(
        "rows=list(csv.DictReader((root/'results/summary.csv').open()))\nfor row in rows: print(row)\ndisplay(Image(filename=str(root/'results/audit.png')))"
    ),
    nbf.v4.new_markdown_cell("## Comprobaciones"),
    nbf.v4.new_code_cell(
        "from src.conformal import TailCalibrator\nassert TailCalibrator([1.,2.,2.,3.]).p_value(2)==.8\nassert not TailCalibrator([0.]*9).alert(100,.05)\nassert metrics['hypothesis_passed']\nprint('Checks passed; sparse abstains, drift invalidates nominal calibration.')"
    ),
    nbf.v4.new_markdown_cell(
        "## Conclusiones y límites\nLa dispersión distinta hace que un umbral global reparta mal las falsas alertas. Calibrar por canal corrige el escenario estacionario al coste de cambiar potencia por canal. No es una contribución teórica nueva: es una auditoría incremental del pipeline KYC. Deriva y pocos ejemplos muestran fallos intencionales. Siguiente paso: validar temporalmente con etiquetas aprobadas y carga de revisión humana."
    ),
]
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nbf.validate(nb)
shell = InteractiveShell.instance()
shell.user_ns.clear()
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
nb.metadata["execution"] = {
    "mode": "IPython in-process sequential run_cell",
    "reason": "ZeroMQ kernel launch unavailable in sandbox; all cells executed, not synthesized",
}
nbf.write(nb, root / "notebook.ipynb")
