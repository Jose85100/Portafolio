"""Execute transport notebook sequentially in fresh IPython process."""

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
        "# Transportar suficientes estadísticas a C++20\n## Pregunta y continuidad\nAyer fusionamos autoescalas en Python. Hoy un productor Python exporta un resumen hexadecimal; un ejecutable C++ lo consume y devuelve estado más SD. La utilidad es conectar componentes y reducir bytes sin trasladar filas. No hay nuevo estimador ni promesa de speedup.\n# Transporte de resúmenes: qué se conserva y qué se pierde\n\n## Original y brecha\nEl programa conserva Welford desplazado29, escala externa30, autoescala31 y fusión Chan entre escalas1nov. El resumen es (n,e,a,b,Q,i): n conteo, e exponente entero, a origen, b media relativa, Q suma centrada normalizada, i indica si hubo algún dato no nulo. Para y=x/2^e, μ_y=a+b y Q=Σ(y−μ_y)². Datos x tienen unidades U; y,a,b,Q son adimensionales. μ_x=2^e(a+b), V_d=2^{2e}Q/(n−d), SD_d=2^e sqrt(Q/(n−d)), d∈{0,1}, n>d. No hay un nuevo estimador.\n\nLa limitación del1nov era una API sólo en memoria Python. Hoy exportamos suficientes estadísticas numéricas a un consumidor C++20 real. No traducimos notebooks ni eliminamos fórmulas; el notebook enseña el contrato y llama al ejecutable.\n\n## Identidad de serialización\nUn binary64 finito representable es x=s·M·2^k con s∈{−1,1}, M entero de hasta53bits y k entero. `float.hex()` escribe esos bits como mantisa hexadecimal y exponente binario; cuatro bits por dígito hexadecimal evitan redondeo decimal de transporte. `float.fromhex` y `strtod` sobre la salida de exportación reconstruyen el mismo double bajo el toolchain probado. Se exige binary64 y redondeo habitual; no se demuestra equivalencia para toda implementación de C++.\n\nEl protocolo local es una línea ASCII con siete campos: `MOMENTS_V1 n e a_hex b_hex Q_hex initialized`. Exporta estado numérico, no contador histórico de reescalados o pérdidas. Al importar, esos diagnósticos se reinician a0; esto es explícito y evita confundir un resumen transportado con su trazabilidad completa. Datos originales, identidad de filas, autenticidad, firma y procedencia no están codificados.\n\n## Derivación de la operación consumida\nPara resúmenes disjuntos A,B, E es el mayor exponente entre resúmenes no nulos; un chunk de ceros no fija unidad. c_j=2^{e_j−E}; y'_j=c_jy_j. La media es lineal: a'_j=c_ja_j, b'_j=c_jb_j. Las diferencias centradas escalan por c_j, por lo que Q'_j=c_j²Q_j. Entonces:\n$$a'_j=2^{e_j-E}a_j,\\quad b'_j=2^{e_j-E}b_j,\\quad Q'_j=2^{2(e_j-E)}Q_j.$$\n$$\\delta=(a'_B-a'_A)+(b'_B-b'_A),\\quad n=n_A+n_B,$$\n$$a=a'_A,\\quad b=b'_A+\\delta\\frac{n_B}{n},\\quad Q=Q'_A+Q'_B+\\delta^2\\frac{n_A n_B}{n}.$$\nLa última identidad sigue de separar Σ_A(y−μ)²=Q_A+n_A(μ_A−μ)² y B análogo: los términos cruzados son0 porque las desviaciones respecto de la media de cada grupo suman0. Sustituyendo μ_A−μ=−δn_B/n y μ_B−μ=δn_A/n se obtiene el término adicional. Es Chan conocido, no una fórmula científica nueva. `moments.hpp::merge` reproduce la operación después de parsear snapshots; `result_json` devuelve SD/varianza con los mismos estados de abstención que Python.\n\n## Dominio y límites\nConteo 0≤n≤2^53−1; la suma de conteos no debe exceder ese máximo. Exponente −1073..1024, componentes finitos, |a|≤1, |b|≤2, 0≤Q≤4n. Estado vacío o sin dato no nulo exige exponent0 y componentes0. Son validaciones estructurales conservadoras, no prueba de que un estado provino de observaciones reales. El consumidor asume snapshots de productores válidos y particiones disjuntas; no identifica solapamiento ni valida causalidad/independencia.\n\nEn reales se conservan conteo, media y suma centrada. En máquina, serialización exacta no vuelve exacta la aritmética posterior ni recupera bits ya perdidos. Reescalar órdenes extremos puede redondear componentes a0; la pérdida histórica no viaja en este V1. Sólo se transportan estadísticas: no se pueden reconstruir observaciones ni recalcular otro estimando. Casos std_underflow/std_overflow devuelven SDnull; variance_underflow/overflow pueden conservar SD. El test[-minsubnormal,minsubnormal] conserva SDmin; [0,minsubnormal] puede abstenerse porque SDrealmin/2 no cabe. Exportar primero un decimal truncado es una ablación conceptualmente distinta y no se usa para fabricar superioridad.\n\n## Utilidad y coste\nDos resúmenes ocupan un número constante de campos frente a n floats originales; bytes exactos y coste se miden. El proceso C++ se lanza por llamada: el coste de IPC domina, y no hay promesa de aceleración. El valor es conectar resúmenes y evitar reenvío de filas, no ganar a NumPy ni aportar un nuevo resultado estadístico. Ninguna garantía de privacidad diferencial: estadísticas también pueden revelar información.\n"
    ),
    code(
        "import json,math,subprocess,shutil\nfrom pathlib import Path\nfrom IPython.display import display,Image\nfrom src.transport import export_state,import_state\nfrom src.cpp_bridge import consume\nfrom src.benchmark_merge import summary,oracle\nif not Path('.build/moments_consumer').exists():\n    cmake=shutil.which('cmake')\n    assert cmake, 'Install pinned requirements (including cmake) and a C++20 compiler; then bash run.sh'\n    subprocess.run([cmake,'-S','.','-B','.build'],check=True,capture_output=True)\n    subprocess.run([cmake,'--build','.build','-j2'],check=True,capture_output=True)\nprint(json.loads(Path('config_transport.json').read_text()))"
    ),
    md(
        "## Producir, transportar y consumir\nLa línea contiene origen, media relativa y suma centrada en su unidad normalizada, no observaciones. Mostramos el snapshot exacto y la salida del consumidor, con comparación contra el oráculo."
    ),
    code(
        "a=summary([1.,2.,3.]);b=summary([1e200,2e200,3e200])\nwire=export_state(a)\nprint('Snapshot:',wire)\nassert import_state(wire).state==a.state\nmerged,out=consume(a,b,0)\nprint('Estado C++ devuelto:',export_state(merged));print('Resultado C++:',out)\nexpected=oracle([1.,2.,3.,1e200,2e200,3e200],0)\nassert merged.state.n==6 and math.isclose(out['std'],expected,rel_tol=1e-12)"
    ),
    md(
        "## Casos límite y validación estructural\nEl parser rechaza versiones desconocidas y Q negativo. No certifica que un snapshot válido provenga de una muestra real. La SD puede caber cuando su cuadrado no cabe; también hay abstención subnormal."
    ),
    code(
        "tiny=math.ulp(0.)\nfor xs in [[-tiny,tiny],[0.,tiny],[-1.79e308,1.79e308]]:\n    _,out=consume(summary(xs[:1]),summary(xs[1:]),0)\n    print(xs,out)\nassert consume(summary([-tiny]),summary([tiny]),0)[1]['std']==tiny\nassert consume(summary([0.]),summary([tiny]),0)[1]['status']=='std_underflow'\ntry:\n    import_state('MOMENTS_V1 2 0 0x0p+0 0x0p+0 -0x1p+0 1')\nexcept ValueError:\n    print('Q negativo rechazado explícitamente')\nelse:\n    raise AssertionError('invalid snapshot accepted')"
    ),
    md(
        "## Experimento y contraste\n24 escenarios (dos semillas, dos tamaños, tres escalas, dos ddof), tres métodos, cinco repeticiones. Python mide fusión de estados ya construidos; C++IPC incluye exportación, lanzamiento, parseo, operación y retorno. NumPy incluye recorrido offline de datos. Los costes no son kernels equivalentes: se reporta cada alcance y no se afirma aceleración. Hipótesis previas: discrepancia≤max(4ulp,1e−12relativo), roundtrip exacto de campos numéricos, reducción de bytes>10 en n1024."
    ),
    code(
        "results=json.loads(Path('results/transport_summary.json').read_text())\nprint(json.dumps(results,indent=2))\nassert results['gate'] and results['minimum_payload_reduction_n1024']>10\nprint('Primeras3filas:',Path('results/transport_raw.csv').read_text().splitlines()[:4])"
    ),
    code("display(Image(filename='results/transport_audit.png'))"),
    md(
        "## Negativo que no debe ocultarse\nEl proceso nuevo por llamada es más lento. No se midió memoria del hijo C++; tracemalloc sólo cubre Python. V1 no transporta diagnósticos históricos: un contador cero al recibir no prueba ausencia de pérdidas anteriores."
    ),
    code(
        "state=summary([1e-300,2e-300,1e300])\nprint('Pérdidas detectadas antes de exportar:',state.rounded_to_zero)\nreceived=import_state(export_state(state))\nassert received.state==state.state and received.rounded_to_zero==0\nprint('Tras importar:',received.rounded_to_zero,'(historia omitida, no ausencia de pérdida)')\nprint('Costes ns:',results['median_ns'])\nprint('Ahora un consumidor C++ combina resúmenes Python sin recibir filas originales.')"
    ),
    md(
        "## Conclusión y siguiente hito\nAdaptación de ingeniería verificada en casos sintéticos, no innovación científica ni validación operacional. Continuar contrato versionado; ajustar si se requieren diagnósticos/procedencia; cerrar promesa de velocidad por IPC. Próxima comparación: lote de resúmenes en un proceso persistente, sólo si amortiza IPC bajo el mismo presupuesto. Fuentes y alcance: prior_art_transport.md; referencias.bib; informe_transport.md14p y rúbricas."
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
nbf.write(nb, root / "notebook_transport.ipynb")
