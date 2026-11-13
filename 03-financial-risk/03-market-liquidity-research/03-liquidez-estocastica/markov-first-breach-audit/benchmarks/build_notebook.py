"""Create and really execute each code cell sequentially with IPython."""

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
        "# Liquidez: primera ruptura, recuperación y dependencia temporal\n## Resumen\nComparamos IID y Markov persistente con los mismos marginales diarios. La reserva necesaria depende de las secuencias, no solo de la caja al final. Datos sintéticos, objetivo5% arbitrario. Los números se calculan abajo; no es calibración bancaria ni requerimiento regulatorio."
    ),
    nbf.v4.new_markdown_cell(
        "## Modelo y supuestos\n$C_t=C_{t-1}+g(S_t)$ y después $S_{t+1}\\sim P(S_t,\\cdot)$. Flujosg=[+1,−2],π=[.8,.2]. IID tiene ambasfilasπ; persistenteP=[[.95,.05],[.2,.8]]. Se verificaπP=π, así que cada día posee mismos marginales y media+.4.\n\n$\\tau=\\inf\\{t\\ge1:C_t<0\\}$: cero no rompe. El DPvivo absorbe la masa que cruza la frontera. $P(\\tau>H)+\\sum_{t=1}^H P(\\tau=t)=1$. No confundirτ>H con tiempo de ruptura igualaH+1. Absorción mide historia, no política de liquidación."
    ),
    nbf.v4.new_markdown_cell(
        "### Hipótesis y pregunta\nCon reserva6,H20,¿persistencia aumenta primera ruptura≥10pp respectoIID?¿La ruptura persistente supera terminal negativo≥2pp?Son umbrales preespecificados enconfig. No existe una afirmación universal de que toda persistencia aumenta todo riesgo."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport csv,json,math\nfrom IPython.display import display,Image\nfrom src.breach import first_breach,minimum_buffer\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nsummary=list(csv.DictReader((root/'results/summary.csv').open()))\nfor row in summary: print(row)\nprint('Errororáculoexhaustivo',metrics['exhaustive_oracle_error'])\nassert metrics['hypothesis_passed']"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos y resultados\nDPfinito sin sampling estima la probabilidad bajo matrizconocida. MonteCarlo30semillas×20.000draws por modelo aporta un contraste computacional independiente; su variación no cuantifica incertidumbre deP ni de flujosreales. Curva0..40 identifica el mínimo entero que cumpleobjetivo5% dentro del modelo."
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/audit.png')))\ntrials=list(csv.DictReader((root/'results/trials.csv').open()))\nfor name in ['iid','persistent']:\n errors=[float(r['error']) for r in trials if r['model']==name]\n print(name,'MC RMSE primera ruptura',math.sqrt(sum(e*e for e in errors)/len(errors)))\nprint('Flujo esperado por día',metrics['expected_daily_cash_increment'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Contraejemplos y fronteras\nDesde caja1,flujos−2,+3: hay ruptura día1 y recuperación día2. Saldo final positivo no implica haber sobrevivido. ParaH1,ambasmatrices dan el mismo riesgo, porque aún no se usa la persistencia de transición. Con reserva0,H20, la curva persistente44,315% queda por debajo de IID48,880%: no hay orden universal entre matrices. Estos contraejemplos impiden sobregeneralizar el efecto."
    ),
    nbf.v4.new_code_cell(
        "r=first_breach(1,2,[-2,3],[[0,1],[0,1]],[1,0])\nassert r.first_breach==(1.,0.) and r.terminal_negative==0\nassert first_breach(2,1,[-2],[[1]],[1]).breach_probability==0\npi=[.8,.2]\nmodels=[[[.8,.2],[.8,.2]],[[.95,.05],[.2,.8]]]\nassert first_breach(1,1,[1,-2],models[0],pi).breach_probability==first_breach(1,1,[1,-2],models[1],pi).breach_probability\nprint('Casorecuperación',r)\nprint('Checks passed')"
    ),
    nbf.v4.new_markdown_cell(
        "## Interpretación y límites\nEl motorC++ existente ya detecta primera ruptura por trayectoria; esteMVP añade oráculo y persistencia, no corrige ese comportamiento. Las reservas5/22 son del escenario/objetivo. Faltan calibración, líneasdecrédito, reacción de clientes, activosliquidables y múltiplesmonedas. El comparador terminal permite recuperación contrafactual tras déficit: no presume acceso real a financiación."
    ),
    nbf.v4.new_code_cell(
        "for row in csv.DictReader((root/'results/performance.csv').open()):print(row)\nprint('Tiempo/memoriaPython global',metrics['seconds'],metrics['peak_tracemalloc_bytes'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Siguiente iteración\nEvaluar incertidumbre de la matrizP y capacidad de fondeo antes de usar el modelo como soporte de decisión. Cinco fuentes primarias verificadas e informe14p explican alcance y fallos. ElDP es exacto bajo discretización/modelo conocidos hasta precisiónflotante; no garantiza liquidez real."
    ),
]
nb.metadata["kernelspec"] = {
    "display_name": "Python3",
    "language": "python",
    "name": "python3",
}
nb.metadata["execution"] = {
    "mode": "IPython sequential in-process",
    "outputs": "captured from real executed cells",
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
