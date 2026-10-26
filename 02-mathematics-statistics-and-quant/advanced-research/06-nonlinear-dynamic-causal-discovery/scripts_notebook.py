"""Build and really execute the audit notebook in a fresh IPython namespace."""

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
    "scope": "fresh namespace; sequential real execution; errors abort; separate Jupyter kernel not tested",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Confusión temporal: predicción frente a intervención
## Resumen
En un DGP conocido sin efecto causal de X sobre Y, la regresión de Y sobre X rezagado rechaza ausencia de asociación en todas las réplicas n=500. Eso no es error del contraste de asociación: el error sería interpretarlo como causalidad. Controlar el confusor correcto recupera β y una tasa de rechazo cercana a α.
## Contexto y métodos
$$Z_t\sim N(0,1),\quad X_t=0.8Z_{t-1}+u^X_t,\quad Y_t=\beta X_{t-1}+0.8Z_{t-2}+u^Y_t.$$
Innovaciones independientes, $u^X,u^Y\sim N(0,0.5^2)$. Las filas $(X_{t-1},Z_{t-2},Y_t)$ son IID en este caso especial; no se simula un VAR con autocorrelación general.
OLS sin control converge a $\beta+0.64/0.89$, pero bajo intervención emparejada $do(X_{t-1}\leftarrow X_{t-1}+\delta)$ el cambio de Y es $\beta\delta$. Es una identidad del SCM conocido, no una estimación observacional.
Para test de un coeficiente: $F=[(RSS_R-RSS_U)/1]/[RSS_U/(n-p)]\sim F_{1,n-p}$ bajo nulidad, rango completo y errores gaussianos IID independientes del diseño **completo**. Con control correcto esas condiciones se cumplen. No se afirman para la ablación de lag erróneo, que expone Z adyacentes.
### Supuestos e identificabilidad
Confusor observado sin error y lag correcto permiten interpretar β dentro de este SCM. Omitirlo, medirlo con ruido o elegir otro lag no da identificación causal. Ningún rechazo predictivo certifica intervención.
## Datos
Semilla20261025;200 réplicas independientes por n/β. Cuatro métodos comparten cada dataset, por lo que comparaciones entre métodos son pareadas. No son4800 datasets independientes."""),
    code(
        "import json,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\nsummary=json.loads(Path('results/summary.json').read_text())\nsummary['config']"
    ),
    md(
        "## Resultados\nLa tabla siguiente muestra solo n=500. Los intervalos MC de rechazo son Clopper–Pearson sobre200 réplicas por método, no intervalos del efecto causal."
    ),
    code("summary['selected_n500']"),
    code("display(Image(filename='results/audit.png'))"),
    md(
        "### Intervención y controles negativos\nProxy ruidoso no equivale a observar el confusor; añadir un control equivocado tampoco cierra el backdoor. La comparación omitida estima otra cantidad poblacional, no un estimador sesgado de su propio parámetro de asociación."
    ),
    code(
        "from src.confounding import generate,lag_test,paired_intervention\nimport numpy as np\ns=generate(500,0,12)\nassert np.array_equal(paired_intervention(s,1),s.y)\nprint('Asociación:',lag_test(s.y,s.x_lag))\nprint('Control correcto:',lag_test(s.y,s.x_lag,s.z_lag2))\nprint('Intervención SCM nula:',float(np.mean(paired_intervention(s,1)-s.y)))"
    ),
    md(
        "## Comprobaciones\nTests incluyen oracle scipy.linregress, identidad F=t², residualización FWL, invariancia afín y errores de rango/varianza. El umbral registrado no es prueba de calibración universal."
    ),
    code("summary['checks']"),
    md(
        "## Conclusiones\nMás datos concentra la asociación omitida alrededor de0.719 aunque β=0. La mejora local es un banco de falsación reproducible; no un algoritmo nuevo de causal discovery. Componente S2 limitado; nonlinearidad, feedback, PCMCI y datos reales siguen pendientes. Fuentes primarias verificadas y BibTeX en fuentes.md/referencias.bib; informe.md documenta14 puntos, alternativas descartadas y límites."
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
