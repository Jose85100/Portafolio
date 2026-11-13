"""Build and really execute every notebook code cell sequentially in IPython."""

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
        "# Concentración crediticia: distribución finita y cola discreta\n## Resumen\nDos carteras sintéticas con pérdida máxima300 y PD2% difieren en concentración. Resultados calculados abajo: oráculo de Bernoullis independientes vs normal con iguales momentos. Es exacto para el modelo sobre rejilla a precisión flotante, no evidencia de riesgo real."
    ),
    nbf.v4.new_markdown_cell(
        "## Contexto y método\nCada pérdida es $L=\\sum_i w_i D_i$, $D_i\\sim Bernoulli(p_i)$ independientes y $w_i$ entero no negativo. Polinomio generador: $G(z)=\\prod_i[(1-p_i)+p_i z^{w_i}]$. La recurrencia $f_i(l)=(1-p_i)f_{i-1}(l)+p_i f_{i-1}(l-w_i)$ preserva masa. No aproximamos PD ni redondeamos exposiciones dentro del motor.\n\nVaR es inversa izquierda de CDF; ES integra exactamente la masa superior1−q cortando el átomo frontera. No se usa E[L|L≥VaR] indiscriminadamente. El algoritmo ES respeta la convención ya existente en weighted-expected-shortfall-audit; lo nuevo es generar la distribución finita ponderada."
    ),
    nbf.v4.new_markdown_cell(
        "### Supuestos y pregunta falsable\nPD conocidas, independencia, LGD/EAD deterministas incorporadas en pesos y horizonte único. ¿La normal infravalora ES99 concentrado más30%? ¿El PMF discreto coincide con enumeración fraccional con error≤1e−12? Son umbrales ex ante, no claims universales. La correlación sistémica es deliberadamente un caso negativo."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport json,csv,math\nfrom IPython.display import display,Image\nfrom src.loss import independent_pmf,tail,normal_tail\nroot=Path.cwd()\nmetrics=json.loads((root/'results/metrics.json').read_text())\nsummary=list(csv.DictReader((root/'results/summary.csv').open()))\nfor row in summary: print(row)\nprint('Oráculo PMF error máximo:',metrics['max_oracle_pmf_error'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Datos y resultados\nGranular:100 posiciones de pérdida3; concentrada:una de100 y20 de10. Total300 y EL6 en ambas; HHI0,01 vs0,1333. La normal usa sus medias y varianzas propias exactas: comparación entre formas de distribución, no se oculta la varianza distinta. Los30 MonteCarlo usan10.000 draws/semilla y mismo DGP independiente por cartera. Boxplots son variación de estimadores, no confianza en riesgo bancario."
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/audit.png')))\ntrials=list(csv.DictReader((root/'results/trials.csv').open()))\nfor name in ['granular','concentrated']:\n errors=[float(r['es_error']) for r in trials if r['case']==name]\n print(name,'MC RMSE ES99',math.sqrt(sum(e*e for e in errors)/len(errors)))"
    ),
    nbf.v4.new_markdown_cell(
        "## Verificaciones y masa en el cuantil\nEjemplo PMF P(L0)=0,8 y P(L2)=0,2. ES50=0,8, mientras el promedio condicional L≥VaR50 mezcla toda la distribución y da0,4. La cola debe tener exactamente50% de masa, incluyendo0,3 en L0. No interpretar cola discreta como promedio de toda masa en la frontera."
    ),
    nbf.v4.new_code_cell(
        "assert abs(tail([.8,0,.2],.5).es-.8)<1e-12\nassert metrics['hypothesis_concentration_passed']\nassert metrics['oracle_tolerance_passed']\nfor weights in ([3]*100,[100]+[10]*20):\n pmf=independent_pmf(weights,[.02]*len(weights))\n assert abs(math.fsum(pmf)-1)<1e-12\n print('EL=',math.fsum(i*p for i,p in enumerate(pmf)),'tail=',tail(pmf,.99))\nprint('Checks passed')"
    ),
    nbf.v4.new_markdown_cell(
        "## Falsación: dependencia perfecta\nSi todas las100 posiciones de3 incumplen juntas con probabilidad2%, la pérdida es0 o300: VaR99=ES99=300. El motor independiente granular predice18 y19,567. La exactitud numérica del modelo equivocado no protege contra dependencia omitida. No se implementa aquí Vasicek, IRB o un modelo regulatorio."
    ),
    nbf.v4.new_code_cell(
        "print('Shock común verdadero',metrics['negative_common_shock_var'],metrics['negative_common_shock_es'])\nfor row in csv.DictReader((root/'results/performance.csv').open()):print(row)\nprint('Tiempo/bytes pico proceso experimento',metrics['seconds'],metrics['peak_tracemalloc_bytes'])"
    ),
    nbf.v4.new_markdown_cell(
        "## Conclusiones y próximos pasos\nLa normal pierde asimetría y átomos; ni siquiera la cartera granular tiene muchos defaults esperados (solo2), así que no se presupone CLT preciso. El caso concentrado refuta uso automático de aproximación normal. Usar el DP como oráculo limitado para probar motores y cuantificar error numérico; no como certificación de capital. Añadir factor común, control de discretización y datos aprobados requeriría otra iteración. Cinco fuentes verificadas y detalles en informe.md/referencias.bib."
    ),
]
nb.metadata["kernelspec"] = {
    "display_name": "Python3",
    "language": "python",
    "name": "python3",
}
nb.metadata["execution"] = {
    "mode": "IPython sequential in-process",
    "outputs": "captured from actual executed cells; no synthetic kernel outputs",
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
