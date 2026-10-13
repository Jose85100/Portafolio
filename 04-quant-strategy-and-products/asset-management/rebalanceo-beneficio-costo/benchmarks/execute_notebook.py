"""Create and execute narrative notebook from existing real benchmark outputs."""

import os
from pathlib import Path

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT = Path(__file__).resolve().parents[1]
nb = nbformat.v4.new_notebook()
nb.metadata.kernelspec = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.cells = [
    nbformat.v4.new_markdown_cell(
        "# Rebalanceo por beneficio frente a costo\n\nMVP M2: verificación sintética, no validación empírica ni producto.\n\nHipótesis: el filtro reduce rotación frente a MV mensual. No presupone mejorar Sharpe. Ventana 252, paso 21, gamma 5, shrinkage diagonal fijo 0.2, 20 seeds y costos 0/10/50 bps. Todas las decisiones usan r[t-252:t]."
    ),
    nbformat.v4.new_code_cell(
        "import json\nimport pandas as pd\nfrom IPython.display import display, Image\nmetadata=json.load(open('results/metadata.json'))\ndisplay(metadata)"
    ),
    nbformat.v4.new_markdown_cell(
        "## Baseline numérico y brecha\nSe conserva el solver diario original como legacy_mv. La variante corregida normaliza el objetivo y verifica una brecha de primer orden para el QP convexo. Una tolerancia absoluta inadecuada no equivale a evidencia de optimización."
    ),
    nbformat.v4.new_code_cell(
        "display(pd.DataFrame(json.load(open('results/solver_diagnostic.json'))))\nprint(open('results/legacy_stdout.txt').read())"
    ),
    nbformat.v4.new_markdown_cell(
        "## Experimento pareado\nRetornos sintéticos gaussianos con medias distintas por activo; régimen estacionario y cambio de volatilidades a mitad de muestra. La regla omite diferencias esperadas de retorno: este supuesto es una limitación explícita. Costos sobre notional comprado + vendido, antes del retorno. No hay selección de parámetros por resultados."
    ),
    nbformat.v4.new_code_cell(
        "summary=pd.read_csv('results/summary.csv')\ndisplay(summary[summary.cost_bps==10].round(5))\ndisplay(Image(filename='results/wealth.png'))"
    ),
    nbformat.v4.new_markdown_cell(
        "## Incertidumbre y ablaciones negativas\nBootstrap pareado de diferencias entre seeds, 5000 réplicas, seed 20261012; intervalos percentiles descriptivos, sin corrección por comparaciones múltiples. No son intervalos de rendimiento futuro de mercados. El filtro no mejora significativamente el Sharpe frente a MV mensual; el shrinkage no añade beneficio de Sharpe en esta muestra."
    ),
    nbformat.v4.new_code_cell(
        "paired=pd.read_csv('results/paired_bootstrap.csv')\ndisplay(paired[(paired.cost_bps==10)&(paired.metric=='sharpe')])\ndisplay(pd.read_csv('results/scaling.csv'))\nc=json.load(open('results/coverage.json'))\ndisplay(c['totals'])"
    ),
    nbformat.v4.new_markdown_cell(
        "## Conclusión\nLa contribución defendible es la corrección numérica y un benchmark auditable del intercambio entre costos y riesgo. No hay un algoritmo nuevo para la literatura. Sin datos reales, impacto, impuestos, ejecución, liquidez ni validación independiente. Consulte informe.md y referencias.bib."
    ),
]
# Execute real cells in-process: this restricted environment blocks kernel TCP sockets.
# No synthetic outputs: capture actual IPython display MIME bundles and streams.
previous = Path.cwd()
os.chdir(ROOT)
shell = InteractiveShell.instance()
count = 0
try:
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        count += 1
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError("Notebook cell execution failed")
        cell.execution_count = count
        cell.outputs = []
        if captured.stdout:
            cell.outputs.append(
                nbformat.v4.new_output("stream", name="stdout", text=captured.stdout)
            )
        if captured.stderr:
            cell.outputs.append(
                nbformat.v4.new_output("stream", name="stderr", text=captured.stderr)
            )
        for output in captured.outputs:
            cell.outputs.append(
                nbformat.v4.new_output(
                    "display_data", data=output.data, metadata=output.metadata
                )
            )
finally:
    os.chdir(previous)
nb.metadata["execution_method"] = (
    "in-process IPython; cells executed with actual rich output capture"
)
nbformat.write(nb, ROOT / "notebook.ipynb")
print(
    "Executed notebook.ipynb:",
    sum(c.cell_type == "code" for c in nb.cells),
    "code cells with outputs",
)
