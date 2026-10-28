"""Execute28October companion notebook in a fresh IPython namespace."""

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
    md(r"""# Compatibilidad de toda la covarianza latente
## Resumen
El gate de26 comprobaba solo el bloque(X,Z). En18casos poblacionales, acepta cuatro matrices latentes imposibles. La nueva comprobación conjunta las rechaza y conserva los coeficientes cuando la varianza verdadera1se declara correctamente.
## Contexto y métodos
Bajo error clásico independiente $W=Z+v$, se exige
$$S_0=Cov(X,Z,Y)=S-\operatorname{diag}(0,\tau^2,0)\succeq0.$$
Que el bloque de regresores $C=Cov(X,Z)$ sea definido positivo no basta. Si C es PD, el complemento de Schur exige $S_{0,YY}-S_{0,YR}C^{-1}S_{0,RY}\geq0$.
### Supuestos clave
Momentos suministrados/poblacionales, error independiente y varianza externa declarada. PSD es una condición necesaria de compatibilidad; no prueba que esa varianza sea cierta. Float64 con tolerancia1e-10, sin redondeo dirigido.
## Datos
Sin datos empíricos ni MonteCarlo:dosβ(0,.3),nueve varianzas declaradas,18casos exactos. Comparación contra gate26y oráculo independiente Schur."""),
    code(
        "import json,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\nsummary=json.loads(Path('results/joint_summary.json').read_text())\nsummary"
    ),
    md(
        "## Resultados\nSe preserva el experimento26 y su notebook. Este notebook registra solo el incremento28."
    ),
    code(
        "rows=list(csv.DictReader(Path('results/joint_cases.csv').open()))\n[r for r in rows if r['beta']=='0.0' and r['declared_variance'] in ['1.0','1.2','1.24']]"
    ),
    code("display(Image(filename='results/joint_audit.png'))"),
    md(
        "## Controles negativos\nUna varianza falsa0.5es compatible y pasa ambos gates; no se presenta aceptación como validación causal."
    ),
    code(
        "from src.joint_gate import correct_covariance_joint\nfrom src.moments import population_covariance\ns=population_covariance(0)\nfalse=correct_covariance_joint(s,.5)\nassert false.status=='accepted' and abs(false.slope)>.4\nassert summary['impossible_accepted_baseline']==4\nassert summary['impossible_accepted_joint']==0\nprint('Varianza falsa pero compatible:',false)"
    ),
    md(
        "## Conclusiones\nSe cierra una brecha de validación de momentos del26, sin reconstruir ni contar como entregado el intervalo27 que no tenía publicaciónGit. PrototipoS2, no solución general de identificación ni CI estadístico. Cinco fuentes primarias reabiertas28; informe_joint.md contiene derivación, tresideas y14puntos."
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
nbf.write(nb, root / "notebook_joint.ipynb")
