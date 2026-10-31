"""Execute dynamic-scale teaching notebook sequentially; no hidden state."""

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
        "# Escala dinámica31: cómo conservar una SD representable\n## Pregunta y resumen\nContinuamos Welford29 y escala externa30: ¿podemos adaptar unidades online sin inspeccionar datos futuros? Benchmark sintético45casos, contra Decimal100, y casos adversos. No se propone un nuevo estimador. NumPy escalado conserva ventaja temporal.\n## Teoría y derivación\n# Escala dinámica: identidad, unidades y límites\nSea x en unidades U, n entero, e un exponente entero y y=x/2^e sin unidades. El núcleo Welford desplazado29 conserva origen a, media relativa b y M2=Σ(y−ȳ)². Su recurrencia conocida es δ=(y−a)−b, b'=b+δ/(n+1), M2'=M2+δ((y−a)−b'). No proponemos una fórmula estadística inédita.\n\nLa limitación30 era necesitar e externo y rechazar un flujo con escalas muy distintas. Proponemos seleccionar e_t=max_{i≤t,x_i≠0} frexp(x_i).exponent; ceros iniciales no fijan escala. Así |y_i|≤1 para el máximo observado. Cuando llega una escala mayor e', definimos c=2^(e−e')≤1. Paso1: y'_i=cy_i. Paso2: a'=ca y b'=cb por linealidad de la media. Paso3: cada diferencia centrada se multiplica por c; entonces M2'=c²M2. Paso4: insertar el nuevo y con el núcleo existente. Esto justifica `ldexp(origin,shift)`, `ldexp(mean_offset,shift)`, `ldexp(m2,2*shift)` en `DynamicMoments.push`.\n\n$$a'=2^{e-e'}a,\\quad b'=2^{e-e'}b,\\quad M_2'=2^{2(e-e')}M_2.$$\n$$V_d=2^{2e}\\frac{M_2}{n-d},\\qquad SD_d=2^e\\sqrt{M_2/(n-d)},\\quad d\\in\\{0,1\\},\\ n>d.$$\nVarianza tiene unidades U²; SD U; conteo, e, y y M2 normalizado sin unidades. Estas identidades son exactas en reales; no constituyen cota de error en máquina. El estado ocupa un número constante de escalares, procesa una pasada; no promete merge entre escalas (API sin merge). No cambian `Moments` ni `scaled_moments`.\n\nDominio finito binary64, n pequeño frente a2^53. Escala seleccionada puede ser1024 (frexp del mayor finito); no materializamos2^e, sino ldexp. En estado normalizado no hay grandes diferencias; no prueba estabilidad universal. Escalado binario exacto mientras representable: al reescalar puede perderse M2 diminuto o un dato bajo el mínimo subnormal. `rounded_to_zero` cuenta tales componentes/observaciones detectadas; no es cota ni conteo de toda información perdida. Cuantización sin llegar a cero sigue posible.\n\nCasos límite: cero/constante→SD0; n≤d error; NaN/inf error; SD no representable→std_underflow/std_overflow; varianza no representable pero SD sí→variance_underflow/variance_overflow. Flujo [0,minsubnormal] tiene SD exacta minsubnormal/2 y redondea0: la salida se abstiene, no inventa éxito. [-minsubnormal,minsubnormal] SD=minsubnormal. Datos redondeados antes de entrada no se recuperan. Bajo orden adverso se acepta redondeo dependiente del orden; no afirmar asociatividad exacta. Sin parámetros aprendidos ni evidencia empírica.\n"
    ),
    code(
        "import math,json,csv\nfrom pathlib import Path\nfrom src.dynamic import DynamicMoments,dynamic_moments\nfrom src.benchmark_dynamic import oracle\nfrom src.scaled import scaled_moments\nfrom IPython.display import display,Image\nprint(json.loads(Path('config_dynamic.json').read_text()))"
    ),
    md(
        "## Traza: el cambio de unidades conserva el problema\nMostramos exponente y M2 normalizado después de cada ingreso. La contribución minúscula puede desaparecer al subir la escala: el contador lo expone sin prometer detectar todos los errores."
    ),
    code(
        "state=DynamicMoments()\nfor x in [1e-300,2e-300,1e300]:\n    state=state.push(x)\n    print(x,state.exponent,state.state.m2,state.rescales,state.rounded_to_zero)\nassert state.rounded_to_zero>0\nprint('SD/1e300',state.result().std/1e300,'oracle',oracle([1e-300,2e-300,1e300])/1e300)"
    ),
    md(
        "## Casos límite y abstención\nLa SD puede caber cuando V no cabe. En el mínimo subnormal, error relativo es una métrica engañosa: comprobamos también4ulp. Si SD real redondea0 se devuelve estado explícito."
    ),
    code(
        "tiny=math.ulp(0.)\nfor xs in [[-tiny,tiny],[0.,tiny],[1e200,2e200],[1e-200,2e-200]]:\n    print(xs,dynamic_moments(xs))\nassert dynamic_moments([-tiny,tiny]).std==tiny\nassert dynamic_moments([0.,tiny]).status=='std_underflow'\nassert dynamic_moments([1e200,2e200]).status=='variance_overflow'"
    ),
    md(
        "## Experimento reproducible y contraste justo\n3seeds×5exponentes×3órdenes,128observaciones,5repeticiones por medición; oráculo Decimal100 sobre float recibido, no decimal ideal. NumPy escalado puede examinar datos completos primero; se mide su normalización, pero no obtiene restricción de una pasada. Comparación útil, no hardware optimizado equivalente. Escala externa0 es ablación de mala configuración, no baseline usado para afirmar superioridad."
    ),
    code(
        "summary=json.loads(Path('results/dynamic_summary.json').read_text())\nprint(json.dumps(summary,indent=2))\nrows=list(csv.DictReader(Path('results/dynamic_raw.csv').open()))\nprint('Primeras3filas:',rows[:3])\nassert summary['gate'] and summary['cases']==45"
    ),
    code("display(Image(filename='results/dynamic_audit.png'))"),
    md(
        "## Negativos: orden, representación e información\nNo recuperamos incrementos ya perdidos por binary64. Una escala creciente preserva identidades reales, pero no asociatividad exacta. No hay garantía universal ni merge dinámico. El estado fijo usa memoria constante en número de escalares; medición de memoria es tracemalloc, no RSS."
    ),
    code(
        "xs=[1e16+i for i in range(4)]\nprint('Entradas recibidas:',xs,'SD',dynamic_moments(xs).std)\nprint('Escala0rechazada:',scaled_moments([1e200,2e200],0))\nprint('NumPy mediana ns:',summary['median_ns']['numpy_scaled'],'dynamic',summary['median_ns']['dynamic'])\nprint('Ahora se procesa un generador sin elegir escala a mano; no hay superioridad universal.')"
    ),
    md(
        "## Fuentes, madurez y siguiente gate\nMatriz prior_art_dynamic.md y referencias.bib. Adaptación de ingeniería verificada con datos sintéticos; no operacional, no nueva fórmula estadística. Próximo: merge entre escalas contra oráculo y pruebas adversas antes de exportar API multilenguaje. Gate pendiente: no ocultar pérdidas de rescalado; estudiar compensación frente a coste medido."
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
nbf.write(nb, root / "notebook_dynamic.ipynb")
