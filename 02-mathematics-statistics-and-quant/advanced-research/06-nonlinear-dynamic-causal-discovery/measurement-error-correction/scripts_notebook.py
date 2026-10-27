"""Execute recovery26 notebook with a fresh IPython shell; no fabricated outputs."""

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
    "scope": "fresh namespace, sequential real execution; separate Jupyter kernel not tested",
    "research_date": "2026-10-26",
    "recovery_execution_date": "2026-10-27",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Error de medida: corrección, selección y fallos
## Resumen
Recuperación de la idea26oct, reconstruida y ejecutada27oct; no se presenta como nueva investigación27. Con n2000 y varianza correcta, RMSE cae a≈.101 frente a≈.560 de OLSproxy. Con n100 empeora a≈.951 frente a≈.570 y se abstiene15veces.
## Contexto y métodos
$X=.8Z+u$, $Y=\beta X+.8Z+e$, $W=Z+v$, con $Var(v)=\tau^2$ conocida externamente, v independiente de(X,Z,Y).
$$C=\begin{pmatrix}S_{XX}&S_{XW}\\ S_{WX}&S_{WW}-\tau^2\end{pmatrix},\qquad \hat\theta=C^{-1}(S_{XY},S_{WY})^T.$$
La primera coordenada estimaβ bajo estos supuestos; no reutilizamos F ni emitimos CI causales sin derivarlos. Una matriz muestral corregida puede no ser definida positiva.
### Supuestos clave
Varianza conocida de una fuente externa, modelo clásico lineal y covarianza válida. Se exige positividad y condición de la correlación corregida<=100. El gate es invariante a unidades, pero no valida la verdad del supuesto.
## Datos
Semilla20261026,200 réplicas por n/β, tamaños100/500/2000, β0/.3, varianzas declaradas0/.5/1/1.5, verdadera1. Son1200datasets y4800evaluaciones pareadas."""),
    code(
        "import json,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\nsummary=json.loads(Path('results/summary.json').read_text())\nsummary['config']"
    ),
    md(
        "## Resultados\nSe comparan errores solo sobre las mismas réplicas aceptadas, informando aparte abstenciones. No equivale a riesgo operacional incondicional."
    ),
    code("summary['n2000']"),
    code("display(Image(filename='results/audit.png'))"),
    md(
        "### Fallos observados\nPoca muestra amplifica el error al invertir momentos. Varianza incorrecta puede producir sesgo grave aunque el gate acepte. El oráculo Z observado dispone de información adicional."
    ),
    code(
        "rows=list(csv.DictReader(Path('results/summary.csv').open()))\n[r for r in rows if r['effect']=='0.0' and r['n']=='100']"
    ),
    md(
        "## Comprobaciones\nOráculos poblacionales, OLS independiente cuandoτ²declarada0, invariancia afín y linealidad en Y, rechazo de entradas inválidas y abstención numérica."
    ),
    code(
        "from src.moments import correct_covariance,population_covariance\nknown=correct_covariance(population_covariance(.3),1)\nwrong=correct_covariance(population_covariance(.3),.5)\nassert abs(known.slope-.3)<1e-12\nassert abs(wrong.slope-.3)>.4\nassert all(summary['checks'].values())\nprint(known,wrong)"
    ),
    md(
        "## Conclusiones\nLa información externa puede identificar una corrección consistente, pero no elimina error de muestra ni arregla supuestos falsos. ComponenteS2 sintético; fuentes, derivación, alcance y14puntos en informe.md. Outputs regenerados27; no se restauraron byteporbyte los del26."
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
