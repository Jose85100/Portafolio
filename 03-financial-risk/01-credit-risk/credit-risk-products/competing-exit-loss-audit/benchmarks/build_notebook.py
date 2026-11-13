"""Build and really execute a small probability-flow notebook in IPython."""

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
        "# Default y prepago: PD condicional no es incidencia acumulada\n## Resumen\nUn motor pequeño conserva población activa y dos salidas competidoras. Datos sintéticos, períodos uniformes y sin afirmación de conformidadIFRS9. El baseline sin prepago representa otro supuesto, no un bug atribuido al repositorio."
    ),
    nbf.v4.new_markdown_cell(
        "## Método y contrato\n$S_0=1$, $D_t=S_{t-1}d_t$, $P_t=S_{t-1}p_t$, $S_t=S_{t-1}(1-d_t-p_t)$. Default y prepago son mutuamente excluyentes dado activo, con d+p≤1. No son hazards independientes continuos ni se ordenan artificialmente dentro delperíodo.\n\n$EL=\\sum_t D_t EAD_t LGD/(1+r)^t$. EAD condicional no debe incluir ya supervivencia/prepago. Todos los parámetros comparten unidadperíodo; no se divide unaPDanual para obtener mensual automáticamente. Hipótesis preespecificada: baseline superaELconjunta≥20% en caso12períodos."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport csv,json,math\nfrom IPython.display import display,Image\nfrom src.model import project\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nprint(json.dumps(metrics,indent=2))\nassert metrics['hypothesis_passed']"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos y resultados\n12períodos,d=.02,p=.10,EAD100,LGD.45,r=.005. Baseline cambia solo prepago a0. Comparación determinista y oráculo racional independiente; no incertidumbre estadística estimada ni parámetros reales."
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/audit.png')))\nfor row in csv.DictReader((root/'results/sensitivity.csv').open()):print(row)\nrows=list(csv.DictReader((root/'results/joint_periods.csv').open()))\nprint('Primero:',rows[0],'Último:',rows[-1])"
    ),
    nbf.v4.new_markdown_cell(
        "## Comprobaciones y casos negativos\nSin prepago,1−S reproducePDlifetime. H1 no presenta diferencia deEL bajo esta convención: no se ha eliminado población antes del primerdefault. Absorción y masa impiden sumar PDcondicionales como si fueran masas marginales."
    ),
    nbf.v4.new_code_cell(
        "r=project([.02]*12,[.10]*12,[100.]*12)\nassert abs(r.default_probability+r.prepayment_probability+r.active_probability-1)<1e-12\nassert abs(project([.02]*12,[0.]*12,[100.]*12).default_probability-(1-.98**12))<1e-12\nassert project([.02],[.10],[100.]).expected_loss==project([.02],[0.],[100.]).expected_loss\nassert metrics['rational_oracle_error']<1e-12\nprint('Mass/oracle/negative checks passed')"
    ),
    nbf.v4.new_markdown_cell(
        "## Interpretación y límites\nEl efecto mantiene PDcondicional yEAD fijas; no modela selección de prepago o riesgo de los sobrevivientes. EAD ya ponderada por salidas duplica ajuste y viola elcontrato. Faltan datos,censura,estimación,recobros,staging y reglas de provisión. La cifra no recomienda disminuir provisiones reales. Cinco referencias primarias verificadas e informe14p separan método de alcanceoperacional. Próxima iteración: contrato de calendario yEADantes de integración."
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
