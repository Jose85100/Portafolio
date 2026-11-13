"""Execute real notebook cells sequentially in process; no socket kernel needed."""

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
        "# Crédito finito: factor común y estabilidad de cola\n## Resumen\nExtendemos el DP25 independiente a dependencia gaussiana, sin cambiar pesos ni PD. Los números se calculan abajo. La integración es numérica; referenciaGH256 no es verdad certificada. Este notebook es un experimento sintético de validación de algoritmo, no de cartera real."
    ),
    nbf.v4.new_markdown_cell(
        "## Modelo y supuestos\n$A_i=\\sqrt{\\rho}Y+\\sqrt{1-\\rho}\\epsilon_i$, independientes Y yε normales. $D_i=1[A_i\\le\\Phi^{-1}(p_i)]$. CondicionadoY=y, $p_i(y)=\\Phi((\\Phi^{-1}(p_i)-\\sqrt{\\rho}y)/\\sqrt{1-\\rho})$. rho es correlación de activoslatentes, no de defaults.\n\n$P(L=l)=\\int f_{DP}(l|y)\\phi(y)dy\\approx\\sum_j(w_j/\\sqrt{2\\pi})f_{DP}(l|y_j)$. Nodos/pesos roots_hermitenorm integran pesoexp(-y²/2). PD conocidas, un factor, LGD/EADdeterministas y rejillaentera. No se redondean pesos aquí."
    ),
    nbf.v4.new_markdown_cell(
        "### Pregunta e hipótesis\n¿ES99 granular sube≥50% respectoindependencia? ¿Últimos órdenes64→128 muestran deltaCDF≤1e−5 ydeltaES≤0,01? Se prueba además ortanteanalítico bivariado. El acuerdo entreórdenes no certifica error global; se incluye un caso donde falla claramente."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport csv,json,math\nfrom IPython.display import display,Image\nfrom src.base import independent_pmf,tail\nfrom src.factor import common_factor_pmf,stability_passed\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nsummary=list(csv.DictReader((root/'results/summary.csv').open()))\nfor row in summary: print(row)\nprint('Oráculo analítico error:',metrics['analytic_orthant_max_error'])\nprint('SHA256 kernel25:',metrics['source_kernel_sha256'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos\nGranular100×3 yconcentrada100+20×10,PD2%,pérdida máxima300,EL6. rho0,2base y0,95stress. GH16/32/64/128 frente256. MonteCarlo20semillas×20.000draws por cartera bajo mismoDGPfactor. Independencia no es una aproximación numérica del modeloρ0,2: es un baseline estructural distinto, incluido para medir su impacto."
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/audit.png')))\ntrials=list(csv.DictReader((root/'results/trials.csv').open()))\nfor name in ['granular','concentrated']:\n errors=[float(r['es_error_vs_reference']) for r in trials if r['case']==name]\n print(name,'MC RMSE ES99 vsGH256',math.sqrt(sum(e*e for e in errors)/len(errors)))"
    ),
    nbf.v4.new_markdown_cell(
        "## Convergencia y referencias independientes\nParaPD1=PD2=.5, rho=.5, P(ambosdefaults)=1/4+asin(rho)/(2π); esta fórmula permite comprobar el cálculo sin compararlo solamente consigo mismo. rho0 vuelve exactamente alDP25. Conservar masa no basta para certificar la cola."
    ),
    nbf.v4.new_code_cell(
        "rho=.5\ntruth=.25+math.asin(rho)/(2*math.pi)\npmf=common_factor_pmf([1,1],[.5,.5],rho,64)\nassert max(abs(a-b) for a,b in zip(pmf,[truth,1-2*truth,truth]))<=1e-12\nassert common_factor_pmf([3,10],[.02,.03],0)==independent_pmf([3,10],[.02,.03])\nassert metrics['hypothesis_passed']\nprint('Independent checks passed')"
    ),
    nbf.v4.new_markdown_cell(
        "## Caso negativo: rho0,95\nLas probabilidadescondicionales se vuelven abruptas y la quadratura moderada oscila. GH256 también es solo una referencia. Si stability_passed=False no debe presentarse la salida como convergida; True sigue siendo solo un diagnóstico local. No hay algoritmo de certificación adaptativo."
    ),
    nbf.v4.new_code_cell(
        "rows=list(csv.DictReader((root/'results/convergence.csv').open()))\nfor row in rows:\n if row['case']=='granular': print({k:row[k] for k in ['regime','nodes','var','es','es_error_vs_reference','stable_vs_previous','mass_error','mean_error']})\nprint('Tiempo global/memoriaPython:',metrics['seconds'],metrics['peak_tracemalloc_bytes'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Interpretación y límites\nEl incrementoES de base demuestra sensibilidad a dependencia, no precisión empírica del parámetro. La cartera concentrada ya tenía gran riesgo idiosincrático; su incremento relativo es menor, sin ser bajo riesgo. Rhoalto requiere otra estrategia de integración. El kernel25se reutiliza sin modificar; cinco fuentes primarias verificadas e informe14p detallan hipótesis, fallos y madurez. Próximo paso: integraciónadaptativa independiente, no publicar másdecimales de un resultado inestable."
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
