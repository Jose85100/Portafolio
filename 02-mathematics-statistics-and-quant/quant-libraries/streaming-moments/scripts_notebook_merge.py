"""Execute merge notebook in a fresh IPython process, sequential abort-on-error."""

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
    "executor": "IPython in-process, fresh process, sequential abort-on-error",
    "scope": "no isolated Jupyter kernel claimed",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(
        "# Fusionar unidades sin perder el significado\n## Pregunta y continuidad\n¿Cómo conectar resúmenes producidos por la autoescala31 sin imponer una escala global previa? Se implementa reescalado+Chan conocido y se auditan órdenes, subnormales y costes. No se afirma innovación disciplinar.\n# Fusionar resúmenes en unidades diferentes\n## Pregunta, notación y original\nContinuamos29Welford/Chan,30escalaexterna,31autoescala. Un resumen de observaciones finitas disjuntas A tiene n_A, exponente e_A, origen a_A, media relativa b_A y suma centrada Q_A, en unidades normalizadas y=x/2^{e_A}. Media μ_A=a_A+b_A. En unidades físicas U, media2^{e_A}μ_A, varianza U², SD U; n y exponentes adimensionales. Asumimos n≪2^53. El contrato no detecta solapamiento: el consumidor garantiza particiones disjuntas.\n\nLa expresión original Chan conocida (doi10.1080/00031305.1983.10483115) sobre la misma unidad es\n$$\\delta=\\mu_B-\\mu_A,\\quad \\mu=\\mu_A+\\delta n_B/(n_A+n_B),$$\n$$Q=Q_A+Q_B+\\delta^2 n_A n_B/(n_A+n_B).$$\nPara derivar, separe Σ_A(y−μ)²=Σ_A[(y−μ_A)+(μ_A−μ)]². El término cruzado es0 porque Σ_A(y−μ_A)=0. Por tanto es Q_A+n_A(μ_A−μ)². Análogo B. Sustituya μ_A−μ=−δn_B/n y μ_B−μ=δn_A/n; suma de cuadrados extra δ²[n_A n_B²+n_B n_A²]/n²=δ²n_A n_B/n. No existe nuevo estimador.\n\n## Brecha y adaptación al estado31\nNo se pueden fusionar Q_A y Q_B en escalas diferentes directamente. Elegimos E=max(e_A,e_B) entre resúmenes con algún dato no nulo: los ceros no determinan unidad. Si ambos son todo ceros E=0. Sea c_j=2^{e_j−E}. Cada y'_j=c_jy_j, luego a'_j=c_ja_j, b'_j=c_jb_j, Q'_j=c_j²Q_j (derivación31 conservada). Ahora ambas medias están expresadas en la misma unidad y se aplica Chan anterior.\n$$a'_j=2^{e_j-E}a_j,\\quad b'_j=2^{e_j-E}b_j,\\quad Q'_j=2^{2(e_j-E)}Q_j.$$\n$$\\delta=(a'_B-a'_A)+(b'_B-b'_A),\\quad n=n_A+n_B,$$\n$$a=a'_A,\\ b=b'_A+\\delta n_B/n,\\ Q=Q'_A+Q'_B+\\delta^2 n_A n_B/n.$$\nEsto corresponde exactamente al helper rebase y `Moments.merge`. Se calcula SD=2^E sqrt(Q/(n−d)), V=2^{2E}Q/(n−d), d∈{0,1}, n>d. Resumen vacío es identidad; n siempre suma. En aritmética real se conservan media, suma centrada, positividad y asociatividad/commutatividad del resultado estadístico. En máquina NO se conserva igualdad bit a bit por orden de reducción; tampoco se garantiza cota universal de error. Constantes/cero producen SD0. NaN/inf se rechazan al push, d/n inválidos al result.\n\n## Condiciones, negativos y propiedades perdidas\nPara resúmenes creados mediante API (no estados construidos arbitrariamente), normalización limita magnitudes. Reescalado puede redondear componentes a0; rounded_to_zero suma diagnósticos anteriores y nuevos, pero no mide toda información perdida ni cota de error. Reutilizar el mismo resumen en ambos lados duplica datos: no independencia ni deduplicación automáticas. La fusión es operación numérica sobre particiones, no inferencia de independencia estadística.\n\nEjemplo adverso: [1e−300,2e−300] fusionado con [1e300,2e300] descarta cantidades pequeñas al reescalar. SD puede seguir representable, pero sus contribuciones no se recuperan. Entradas redondeadas antes de ingresar siguen irrecuperables. Subnormal [-min,min] produce SD=min; [0,min] posee SD realmin/2 y puede abstenerse std_underflow. Resultado depende del árbol de cómputo; no teorema flotante. Ninguna mejora científica original ni implementación paralela; sólo componente conectable con pruebas.\n"
    ),
    code(
        "import json,math,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\nfrom src.dynamic import DynamicMoments\nfrom src.benchmark_merge import summary,oracle,reduce_states\nprint(json.loads(Path('config_merge.json').read_text()))"
    ),
    md(
        "## Construcción de la herramienta paso a paso\nLos chunks pueden venir de motores distintos en el futuro; hoy todoPython, ejecución secuencial. Observe e_A y e_B, la unidad común E y el conteo combinado. Ni almacenar datos originales ni reescanearlos es necesario al fusionar resúmenes."
    ),
    code(
        "left=summary([1.,2.,3.]);right=summary([1e200,2e200,3e200])\nmerged=left.merge(right)\nprint('Exponentes',left.exponent,right.exponent,'común',merged.exponent)\nprint('n=',merged.state.n,'SD/1e200=',merged.result().std/1e200)\nexpected=oracle([1.,2.,3.,1e200,2e200,3e200],0)\nassert merged.state.n==6 and math.isclose(merged.result().std,expected,rel_tol=1e-12)\nassert DynamicMoments().merge(left)==left"
    ),
    md(
        "## Cero y subnormal son contratos distintos\nUn chunk de ceros no debe fijar una escala0 y borrar la SD de datos diminutos. Fixtures hex preservan exactamente datosbinary64 recibidos para futuros contratos multilenguaje, aún no implementados."
    ),
    code(
        "tiny=math.ulp(0.)\nz=summary([0.,0.]);s=summary([-tiny,tiny])\nprint('Cero+subnormal',z.merge(s).result())\nprint(json.loads(Path('fixtures_merge.json').read_text()))\nassert s.result().std==tiny\nassert z.merge(s).exponent==s.exponent\nassert summary([0.]).merge(summary([tiny])).result().status=='std_underflow'"
    ),
    md(
        "## Benchmark, sensibilidad y justicia del contraste\n48escenarios:2seeds×2n×3exponentes×2chunks×2ddof.5métodos,240filas. Umbral previo max(4ulp,1e−12relativo), Decimal100. Merge_left/tree miden sólo fusión precomputada; merge_tree_full incluye construirchunks y es comparable al recorrido serial. NumPy escalado incluye normalización y permanece baseline competitivo, con disponibilidadoffline no restricción streaming. No ejecución paralela ni speedup declarado."
    ),
    code(
        "results=json.loads(Path('results/merge_summary.json').read_text())\nprint(json.dumps(results,indent=2))\nrows=list(csv.DictReader(Path('results/merge_raw.csv').open()))\nprint('Primeras5filas',rows[:5])\nassert results['gate'] and results['scenario_count']==48\nprint('Costecompleto ns',results['median_ns']['merge_tree_full'],'serial',results['median_ns']['serial_dynamic'],'NumPy',results['median_ns']['numpy_scaled'])"
    ),
    code("display(Image(filename='results/merge_audit.png'))"),
    md(
        "## Negativos: no asociatividad bit a bit y pérdida\nSe explora diferencia entre árboles sobre los mismos datos sin escoger el árbol tras ver resultados. Ninguna identidad real garantiza bitsiguales. No duplicar un resumen para simular una partición disjunta; es responsabilidad del consumidor."
    ),
    code(
        "index={(r['seed'],r['n'],r['exponent'],r['chunks'],r['ddof'],r['method']):r for r in rows}\ndifferent=0\nfor key,row in index.items():\n    if key[-1]=='merge_left':\n        other=index[key[:-1]+('merge_tree',)]\n        different+=float(row['sd'])!=float(other['sd'])\nprint('Diferencias binariasleft/tree:',different)\na=summary([1e-300,2e-300]);b=summary([1e300,2e300]);c=a.merge(b)\nprint('Componentesredondeadosa0diagnóstico:',c.rounded_to_zero)\nassert c.rounded_to_zero>0\nprint('Duplicarresumen aumenta n:',a.merge(a).state.n,'no es deduplicación')"
    ),
    md(
        "## Decisión y siguiente hito\nContinuar: permite combinación incremental de resúmenes sin elegir unidadexterna. Adaptación de ingeniería, prototipo verificado en escenarios sintéticos, no operacional. Ajustar ante redondeo, cerrar superioridad universal. Siguientegate: equivalencia multilenguaje usando fixtureshex y prueba de límites antes de exportar API. Matrizfuentes prior_art_merge.md; informe_merge.md14p y rúbricas. Se conserva todo29–31 sin reemplazar fórmulas/notebooks."
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
nbf.write(nb, root / "notebook_merge.ipynb")
