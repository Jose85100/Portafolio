"""Execute the reduction-order research notebook with a fresh IPython namespace."""

from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from src.benchmark_reduction import run

root = Path(__file__).resolve().parent
run()
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}
nb.metadata.execution = {
    "executor": "IPython in-process, fresh namespace",
    "isolated_kernel": False,
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Orden de reducción y error de redondeo

## Pregunta y continuidad
La línea MOMENTS ya permite fusionar particiones mediante Chan después de rebasing dinámico. En reales, la fusión representa una operación asociativa; en binary64, cada suma y producto se redondea y el árbol puede cambiar el resultado. Comparamos el fold secuencial, el orden inverso y un árbol balanceado fijo. Este experimento es un audit de ingeniería; no propone una nueva estimación.

## Fórmula y brecha
Para resúmenes A,B de particiones disjuntas, con medias $\mu_A,\mu_B$, conteos $n_A,n_B$ y sumas centradas $Q_A,Q_B$:
$$\delta=\mu_B-\mu_A,\quad \mu=\mu_A+\delta n_B/n,\quad Q=Q_A+Q_B+\delta^2 n_An_B/n.$$
La derivación expande $\sum (x_i-\mu)^2$ por grupo; los términos cruzados desaparecen por centrado. En máquina, Chan permanece estable frente a la fórmula ingenua, pero no vuelve bitwise asociativo al operador. La herramienta fija una estructura reproducible: pares adyacentes se fusionan por nivel y un resumen impar pasa al nivel siguiente.

## Hipótesis falsable y diseño
En entradas sintéticas alrededor de $10^8$, con desviación de orden $10^{-2}$, el árbol balanceado debe quedar dentro de `max(4 ulp, 1e-12 relativo)` del oráculo Decimal de los mismos float64. El benchmark compara tres órdenes, 3 semillas y n=256/4096, chunks de 32. Tiempo es sólo el merge tree, excluye lectura y construcción de chunks. La semilla y la configuración están fijadas en `config_reduction.json`.

## Límites
El orden balanceado determina un resultado repetible para el mismo orden de chunks, no invariancia a permutaciones ni error universal. Se asume que los resúmenes son disjuntos; la API no deduplica. Los datos son sintéticos, no evidencia empírica."""),
    code("""from src.benchmark_reduction import run
summary = run()
assert summary["rows"] == 18"""),
    md(
        "La figura compara desviaciones estándar finales para tres semillas. Diferencias visibles reflejan sensibilidad al orden bajo precisión finita, no diferencias en el estimando poblacional."
    ),
    code("""import json
from pathlib import Path
print((Path('results/reduction_summary.json')).read_text())
assert Path('results/reduction_order.png').exists()"""),
]
shell = InteractiveShell()
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_in_exec or result.error_before_exec:
        raise RuntimeError(f"Notebook cell {i} failed")
    cell.execution_count = i + 1
    if captured.stdout:
        cell.outputs.append(
            nbf.v4.new_output("stream", name="stdout", text=captured.stdout)
        )
    if result.result is not None:
        cell.outputs.append(
            nbf.v4.new_output(
                "execute_result",
                execution_count=cell.execution_count,
                data={"text/plain": repr(result.result)},
                metadata={},
            )
        )
nbf.write(nb, root / "notebook_reduction.ipynb")
