"""Author and actually execute the narrative; no pasted simulated outputs."""

import os
from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb = nbf.v4.new_notebook(
    cells=[
        md(r"""# Fire-Sale Price Audit
## tl;dr
Un solo precio terminal no agota el conjunto de equilibrios. Este componente S2
enumera regímenes de liquidación de un activo con demanda inversa lineal y piso.
La multiplicidad no es una contribución teórica nueva: el aporte es el censo
reproducible de raíces, los controles de tangencia y la comparación con el repo.
El programa Sovereign–Bank Strategic Nexus sigue **S2 parcial**: no hay un gobierno
estratégico ni estimación de precios soberanos o de probabilidad de crisis."""),
        md(r"""## Context & Methods
### Pregunta, alternativas y umbrales
¿Cuánto riesgo de selección oculta el stress a precio fijo o una iteración desde
el precio fundamental? H1: el fixture de dos bancos debe producir exactamente
precios .05, .2 y .8 con error absoluto ≤1e-10; la iteración superior omite dos.
H2: con financiación total .3125 existe una raíz doble en .5 que debe recuperarse.
Un contraejemplo invalida la generalización del resultado: no basta dibujar una
curva que parezca converger. Los controles sin impacto o con caja suficiente
deben recuperar únicamente q=1. Las barreras son convenciones experimentales,
no significación estadística ni estimación causal."""),
        md(r"""### Key Assumptions y mecanismo económico
Cada banco i tiene caja c_i, deuda vencida D_i y s_i unidades de un activo común.
Toda la deuda es externa; los pagos interbancarios se **excluyen** en este módulo.
El activo puede representar una cartera soberana homogénea, pero no se modelan
default soberano, plazo ni riesgo fiscal. Sin ventas cortas, compras bancarias,
colateral, crédito de emergencia ni costos de quiebra. Agentes precio-aceptantes
obedecen una regla mínima, no resuelven un juego de liquidación.
$$d_i=(D_i-c_i)^+,\quad \gamma_i(q)=\min(s_i,d_i/q),$$
$$F(q)=\max(q_{min},q_0-a\sum_i\gamma_i(q)),\quad q=F(q).$$
Todas las unidades se venden al mismo precio uniforme final q. No son ingresos
integrados bajo una curva marginal de ejecución. El piso supone demanda externa
perfectamente elástica allí, no un rescate gratuito demostrado factible.
La misma ecuación puede representar ventas simultáneas, pero la iteración de
Picard no es una dinámica económica estimada."""),
        code(
            "import sys,json,csv\nfrom pathlib import Path\nfrom dataclasses import replace,asdict\nsys.path.insert(0,str(Path('src').resolve()))\nfrom market import Market,equilibria,iterate,balance,update\nm=Market((0.,0.),(.1,.1),(1.,1.),.8)\nfor r in equilibria(m): print(asdict(r),balance(m,r.price))"
        ),
        md(r"""### Formulación por tramos y alcance de la enumeración
Los quiebres ocurren en q=d_i/s_i para s_i>0. En cada intervalo el conjunto S
de bancos que vende toda su cartera es fijo. Definiendo
$$A=\sum_{i\in S}s_i,\quad B=\sum_{i\notin S}d_i,$$
la condición interior equivale a
$$q^2-(q_0-a A)q+a B=0.$$
Se evalúan ambos candidatos de cada cuadrática, se verifica pertenencia al tramo,
se añade el piso solo si F(piso)=piso y se eliminan duplicados. Esa reducción
algebraica es elemental y válida para **este** modelo; no prueba exhaustividad
del modelo multiactivo de la literatura. El código calcula signos del
discriminante con Fraction de los strings decimales y raíces con Decimal(64).
Los precios publicados son float. No hay redondeo dirigido ni certificación
formal; se rechazan raíces distintas con separación <1e-10.
El costo implementado O(n²) prioriza claridad y no es un solver industrial."""),
        code(
            "roots=equilibria(m)\nprint('Raíces enumeradas:',[r.price for r in roots])\nprint('Picard superior e iteraciones:',iterate(m,1.))\nprint('Picard inferior:',iterate(m,m.floor))\nprint('Una sola actualización:',update(m,1.))\nprint('Baseline precio fijo:',balance(m,1.))\nassert [round(r.price,10) for r in roots]==[.05,.2,.8]"
        ),
        md(r"""### Estabilidad, selección y refutación de unicidad
En un tramo sin piso, F'(q)=aB/q². La etiqueta estable se refiere únicamente a
atracción local de esa iteración (pendientes de ambos lados <1), no estabilidad
macroeconómica, bienestar ni selección racional de equilibrio. En el fixture,
las pendientes son 0,4,.25. Los inicios extremos encuentran las dos soluciones
estables, pero no la inestable. Una malla+Brent puede hallar las tres si las
separa; tampoco garantiza ver tangencias o pares más cercanos que su malla.
Para bancos idénticos no saturados, B es la necesidad total de fondos:
$$\Delta=q_0^2-4aB.$$
Con a=.8, q0=1 el pliegue aparece en B=.3125, q=.5. Esto es una identidad
analítica del ejemplo, no una bifurcación empíricamente identificada."""),
        code(
            "fold=replace(m,debt=(.15625,.15625))\nfor delta in [-1e-8,0,1e-8]:\n case=replace(fold,debt=(.15625+delta,)*2)\n print('Cambio por banco:',delta,'precios:',[r.price for r in equilibria(case)])\nprint(Path('results/ablations.csv').read_text())"
        ),
        md(r"""## Data y contabilidad
Todo es sintético, seed20261019. No se descargan balances ni datos de mercado.
No hay identificación de a, q0 ni el piso: son supuestos. No se usa bootstrap
para disfrazar repetición de un escenario determinista como incertidumbre.
$$p_i=\min(D_i,c_i+q\gamma_i),\quad
 E_i=c_i+q\gamma_i-p_i+q(s_i-\gamma_i).$$
De aquí, sum(c_i+q s_i)=sum(p_i+E_i). El impago son promesas contractuales
incumplidas; la pérdida marcada es (q0-q)sum(s_i). No son lo mismo y ninguna
de las dos equivale por sí sola a pérdida social: faltan compradores, utilidad
y valor de tenencia fuera del sector bancario."""),
        code(
            "for r in roots:\n b=balance(m,r.price)\n print('q,ventas,pago,impago,pérdida marcada,identidad:',[b[k] for k in ['price','sales','paid','unpaid','marked_loss','identity_error']])\nprint('Reducción al EN anterior (sin aristas interbancarias):')\nprint(Path('results/repo_regression.csv').read_text())"
        ),
        md(r"""## Results
La figura compara F(q) con la diagonal y muestra todas las ramas de equilibrio
en el barrido de fondos. Son escenarios, no intervalos de confianza. El piso
produce una rama baja cuya existencia depende del supuesto de demanda externa:
subirlo a .3 elimina la solución de default del ejemplo y deja solo .8. Esto
no prueba que apoyar precios sea gratis o mejore bienestar."""),
        code(
            "from IPython.display import Image,display\ndisplay(Image(filename='results/comparison.png'))\nprint(Path('results/numerical_crosscheck.csv').read_text())"
        ),
        md(r"""### Benchmarks y controles negativos
Se mide pared y pico de asignaciones Python con tracemalloc, no RSS ni memoria
nativa total. Tres repeticiones, n=8,32,128 con exposiciones agregadas casi
constantes y heterogeneidad por banco. La enumeración busca **todas** las raíces;
Picard busca una: no se atribuye una mejora de velocidad por resolver problemas
distintos. Malla101+Brent es un baseline numérico independiente, no la
implementación completa de Feinstein. El contraste a malla4001 tiene 40 casos
aleatorios no degenerados y no demuestra exhaustividad para todos los parámetros."""),
        code(
            "rows=list(csv.DictReader(Path('results/costs.csv').open()))\nfor row in rows:\n if row['n']=='128': print(row)\nprint(Path('results/coverage.txt').read_text())\nprint(json.loads(Path('results/metadata.json').read_text()))"
        ),
        md(r"""## Takeaways, fallos y límites
Fallos de desarrollo corregidos: el primer benchmark intentó pasar la clave
price dos veces a dict; la primera invocación del pipeline se lanzó antes de
crear benchmarks. Se conserva el resultado final ejecutado, no se declaran
aquellos intentos como éxitos. Fallos metodológicos intencionales: una única
iteración no es equilibrio, un punto fijo no prueba unicidad y cambios de signo
no detectan todas las raíces dobles. Límites del solver: precisión finita,
complejidad cuadrática y piso positivo obligatorio. No se validó n>128.
La combinación simultánea con red EN, colateral y un gobierno estratégico sigue
pendiente; la regresión EN solo comprueba la reducción sin enlaces.
Ver informe.md, referencias.bib y results/search_log.md para fuentes consultadas,
bloqueos y límites de la revisión. No se afirma prioridad científica ni S3."""),
    ]
)
nb.metadata.kernelspec = dict(
    display_name="Python 3", language="python", name="python3"
)
nb.metadata.execution_method = "Actual IPython in-process; captured stdout and images"
os.chdir(root)
shell = InteractiveShell.instance()
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError("Notebook execution failed")
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
