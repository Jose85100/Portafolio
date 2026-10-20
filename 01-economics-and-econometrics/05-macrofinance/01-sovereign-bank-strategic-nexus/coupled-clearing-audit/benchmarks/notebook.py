"""Build the economic narrative and actually execute every code cell."""

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
        md(r"""# Coupled Clearing Audit
## tl;dr
Un único stress a precio fijo no describe el conjunto de soluciones del mecanismo
de liquidación mínima. Este componente **S2** conecta cobros interbancarios,
necesidad de caja y precio del activo. El ejemplo asimétrico tiene tres puntos
fijos; en la rama baja el impago externo es .12, no .06 como sugiere congelar
cobros contractuales. Esa ablación no es factible como equilibrio conjunto.
El aporte es incremental del repo, no un modelo teórico nuevo ni evidencia bancaria.
El programa soberano–bancario permanece S2 parcial, sin gobierno estratégico."""),
        md(r"""## Context & Methods
### Pregunta falsable, vertientes y umbral
¿Ignorar el incumplimiento de las contrapartes cambia precios y pérdidas de
liquidez? H1: recuperar los tres precios analíticos del fixture con error≤1e-10
y residual conjunto≤1e-9. H2: congelar cobros contractuales subestima el impago
externo de la rama baja en al menos .05 y viola factibilidad de balance.
Comparaciones condicionales, siguiendo THEORY_COMPARISON_PROTOCOL.md:
1. **EN a precio fijo**: resuelve pagos para un precio exógeno; no promete resolver el mercado.
2. **Cobros contractuales congelados**: supone que todos los deudores pagan nominal;
   puede ser una hipótesis válida sin defaults, pero falla cuando sí los hay.
3. **EN + liquidación mínima**: ambos precios y pagos se determinan conjuntamente.
No se comparan escuelas por preferencia doctrinal. La predicción discriminante
es el shortfall y la viabilidad de pagos, no una correlación observada."""),
        md(r"""### Key Assumptions y datos
Una fecha, un activo homogéneo, bancos precio-aceptantes y obligaciones nominales
fijas. L_ij es lo que i debe a j, o_i deuda a acreedores externos,
\(\bar p_i=\sum_jL_{ij}+o_i\), \(\Pi_{ij}=L_{ij}/\bar p_i\).
Caja c_i y stock s_i son exógenos. Se usa caja antes de vender; no se vende
más del stock ni se compra otro activo. Toda venta ejecuta al precio uniforme
final q: no se integra una curva marginal de VWAP. Sin colateral, deuda nueva,
costos de quiebra, garantía pública ni default soberano endógeno.
Contrato del solver:1–4 bancos, ancla externa≥1% de la deuda de cada deudor,
piso≥1e-6 e inputs finitos≤100. Son límites técnicos, no parámetros estimados.
El piso es demanda externa elástica postulada, no rescate gratuito.
Todo es sintético, seed20261020; no hay estimando empírico identificado."""),
        code(
            "import sys,json,csv,math\nfrom pathlib import Path\nfrom dataclasses import replace\nimport numpy as np\nroot=Path('.').resolve()\nsys.path[:0]=[str(root/'src'),str(root.parent/'sovereign-clearing-audit/src'),str(root/'benchmarks')]\nfrom coupled import Economy,census,accounts\nfrom clearing import Network,rational_clear\nfrom run import frozen\nconfig=json.loads(Path('results/config.json').read_text())\ne=Economy(((0.,.1),(.1,0.)),(.1,.1),(0.,.02),(1.,.2),.8)\nprint('Seed:',config['seed'],'; deuda nominal:',e.total,'; Pi:',e.pi)\nroots=census(e)\nfor r in roots: print('q=',round(r.price,12),'pagos=',r.payments,'residual=',r.residual)"
        ),
        md(r"""### Sistema acoplado y por qué los defaults afectan al precio
\[
p_i=\min(\bar p_i,c_i+q s_i+\sum_j\Pi_{ji}p_j),\qquad
\gamma_i(p,q)=\min(s_i,[\bar p_i-c_i-\sum_j\Pi_{ji}p_j]^+/q),
\]
\[q=\max(q_{min},q_0-a\sum_i\gamma_i(p,q)).\]
Si una contraparte paga menos, caen los cobros, aumenta la necesidad de ventas
y puede caer el precio común. No es necesario un juego estratégico para este
feedback contable. Es una reducción de la condición de liquidación mínima de
Feinstein [arXiv1506.00937,Assumption3.1], no un mecanismo inventado hoy.
Con q fijo, el ancla externa hace único al vector EN por contracción en norma1.
Pero no implica unicidad del sistema conjunto: aquí q también cambia.
El mapa conjunto es continuo sobre una caja compacta, por lo que tiene un punto
fijo. Es un argumento estándar de existencia para este modelo, no una nueva
prueba publicada ni una certificación de todo cálculo flotante."""),
        md(r"""### Derivación de la enumeración: tres estados por banco
Cada banco es D(default y vende todo),V(solvente y vende) o Z(solvente sin ventas).
Para D, dados pagos nominales de los solventes:
\[
p_D=(I-\Pi_{DD}^T)^{-1}(c_D+\Pi_{SD}^T\bar p_S+q s_D)=u_D+v_Dq.
\]
Los pagos solventes son \(\bar p_S\). Los cobros resultan afines en q.
Las condiciones default/solvencia y gap positivo/no positivo son desigualdades
lineales en q. Su intersección es un intervalo racional por régimen.
En ese intervalo la venta agregada tiene forma A+B/q; A incluye el stock vendido
por defaults y la respuesta de cobros de los solventes que venden.
Así, el precio interior satisface
\[q^2-(q_0-aA)q+aB=0.\]
Se verifican ambas raíces y el piso, pertenencia al intervalo y residual conjunto.
Los límites pueden pertenecer a varios regímenes: se eliminan duplicados.
Son 3^n regímenes, no un algoritmo escalable. Coeficientes y desigualdades usan
Fraction; sqrt usa Decimal80 y las salidas son float. No hay redondeo dirigido
ni prueba formal de exhaustividad numérica cerca de raíces indistinguibles."""),
        code(
            "expected=[.05,(.92-math.sqrt(.3984))/2,(1+math.sqrt(.424))/2]\nassert len(roots)==3\nassert max(abs(r.price-q) for r,q in zip(roots,expected))<1e-10\nassert max(r.residual for r in roots)<1e-9\nprint('Oráculo analítico:',expected)\nprint('Rama baja exacta: pagos13/150 y11/150; impago externo3/25')\nnet=Network(np.array(e.liabilities),np.array(e.outside))\nfor r in roots:\n p=rational_clear(net,np.array(e.cash)+r.price*np.array(e.stock))\n error=max(abs(float(x)-y) for x,y in zip(p,r.payments))\n assert error<1e-10\n print('EN previo al precio candidato: q=',r.price,'error de pagos=',error)"
        ),
        md(r"""## Data y contabilidad
Los recursos del sector a precio q son caja más q por stock inicial. Bajo pagos
pro-rata, los cobros y pagos internos se cancelan al consolidar:
\[\sum_i(c_i+qs_i)=\sum_i(o_i/\bar p_i)p_i+\sum_i E_i.\]
Pero esta identidad algebraica por sí sola también puede cumplirse con E_i<0.
Por eso se comprueban solvencia/factibilidad y residual además de la identidad.
No se usa la identidad como certificado de equilibrio. El impago bruto cuenta
obligaciones internas repetidamente; el impago externo y la pérdida marcada son
distintos y ninguno basta para medir bienestar agregado sin compradores/utilidad."""),
        code(
            "for label,rs in [('acoplado',roots),('cobros congelados',frozen(e))]:\n for r in rs:\n  a=accounts(e,r)\n  print(label,'q=',round(r.price,9),'impago externo=',round(a['outside_unpaid'],9),'min equity=',round(a['min_equity'],9),'residual=',r.residual)\nassert abs(accounts(e,roots[0])['outside_unpaid']-.12)<1e-12\nassert accounts(e,frozen(e)[0])['min_equity']<0\nprint('Contraejemplo: congelar cobros no produce otro equilibrio conjunto viable.')"
        ),
        md(r"""## Results: precisión, sensibilidad y falsaciones
El equilibrio intermedio acoplado .144405 tiene un banco en default y otro
solvente; el precio intermedio con cobros congelados es .109517. La rama alta
.825576 coincide porque todos pagan nominal: control positivo de la reducción.
En la rama baja, congelar cobros da equity mínimo−.035 y residual conjunto .035;
no se presenta como equilibrio alternativo ni como política pública.
Las curvas muestran escenarios, no probabilidades de selección ni intervalos
de confianza. La caja desplaza las ramas condicionalmente al mecanismo supuesto."""),
        code(
            "import io\nimport matplotlib.pyplot as plt\nfrom IPython.display import Image,display\nrows=list(csv.DictReader(Path('results/cash_sweep.csv').open()))\nfig,ax=plt.subplots(figsize=(7,4),layout='constrained')\nfor label,color,marker in [('joint','#22658c','o'),('frozen','#bd781e','x')]:\n selected=[r for r in rows if r['method']==label]\n ax.scatter([float(r['cash_bank1']) for r in selected],[float(r['price']) for r in selected],color=color,marker=marker,s=24,label=label)\nax.set(xlabel='Caja del banco1 (numeraire)',ylabel='Precio',title='Acoplamiento frente a cobros nominales congelados')\nax.legend();ax.grid(alpha=.15)\nbuffer=io.BytesIO();fig.savefig(buffer,format='png',dpi=140);plt.close(fig)\ndisplay(Image(data=buffer.getvalue()))"
        ),
        md(r"""### Robustez, hipótesis rivales e identificación pendiente
Con impacto cero se recupera EN al precio1. Sin enlaces se recupera el MVP de
ayer. Caja suficiente elimina las ventas, y el ejemplo simétrico conserva los
precios .05,.2,.8. Un pliegue sin enlaces vuelve a revelar el fallo de una malla
basada en cambios de signo: no refuta un teorema de unicidad cuyas hipótesis no
se satisfacen. El modelo tampoco identifica contagio causal observacional:
un factor común puede producir pérdidas simultáneas sin enlaces. Harían falta
balances granulares, exposición predeterminada y un shock exógeno de liquidez
para distinguir esos mecanismos; no se ejecutó ese estudio ni se afirma causalidad."""),
        code(
            "rng=np.random.default_rng(20261020)\nfor bump in rng.choice(np.arange(0,8)/100,size=5,replace=False):\n case=replace(e,cash=(float(bump),.02))\n assert census(case)[-1].price>=roots[-1].price-1e-9\nprint('Cinco perturbaciones deterministas de caja: monotonicidad de la mayor raíz pasa.')\nprint(Path('results/ablations.csv').read_text())\nchecks=list(csv.DictReader(Path('results/nested_crosscheck.csv').open()))\nprint('Contrastes independientes:',len(checks),'máxima diferencia:',max(float(r['max_grid_to_enum_error']) for r in checks))"
        ),
        md(r"""### Costos, no superioridad general
La enumeración y la malla buscan múltiples raíces; la iteración superior solo
busca una. No se comparan como tareas equivalentes. Se usa una reducción con
stock y deuda externa agregados constantes para n2/3/4,3 repeticiones.
Se reporta tiempo de pared y pico de asignaciones Python con tracemalloc, no
RSS ni memoria nativa total. La complejidad exponencial impide extrapolar a
128 bancos: se rechaza n>4, no se simula haber validado ese tamaño."""),
        code(
            "import statistics\nrows=list(csv.DictReader(Path('results/costs.csv').open()))\nfor method in sorted({r['method'] for r in rows}):\n selected=[r for r in rows if r['method']==method and r['n']=='4']\n print(method,'mediana segundos=',statistics.median(float(r['seconds']) for r in selected),'pico Python mediano=',statistics.median(int(r['python_peak_bytes']) for r in selected),'raíces=',selected[0]['roots_recovered']+'/'+selected[0]['reference_roots'])\nprint(Path('results/coverage.txt').read_text())\nprint(json.loads(Path('results/metadata.json').read_text()))"
        ),
        md(r"""## Takeaways y bibliografía
Se cerró un acoplamiento antes pendiente con un caso pequeño ejecutable, no el
programa dinámico completo. Persisten S1:colateral, préstamo, gobierno, feedback
fiscal e identificación. El solver es S2; estos tests no elevan el programa a S3.
Límites:regímenes exponenciales, piso exógeno, precios uniformes y precisión finita.
Fallos corregidos durante desarrollo:imports locales sin excepción E402 y rutas
de lectura iniciales incorrectas al revisar el nuevo auditor estático. No fueron
fallos económicos ni validaciones exitosas. Los resultados guardados corresponden
al pipeline final. Ver informe.md para cobertura medida, fallos y sesgos.
Referencias verificadas: Eisenberg–Noe(2001), DOI10.1287/mnsc.47.2.236.9835;
Feinstein, https://arxiv.org/abs/1506.00937 ; Cifuentes–Ferrucci–Shin,
https://www.bankofengland.co.uk/working-paper/2005/liquidity-risk-and-contagion .
Más fuentes, versiones y enlaces en referencias.bib. No se afirma revisión
exhaustiva ni prioridad científica; bloqueos en results/search_log.md."""),
    ]
)
nb.metadata.kernelspec = dict(
    display_name="Python 3", language="python", name="python3"
)
nb.metadata.execution_method = (
    "Actual IPython in-process; captured streams and rendered PNG"
)
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
        raise RuntimeError("Notebook failed during actual execution")
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
