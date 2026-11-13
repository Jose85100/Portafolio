"""Cumulative tutorial: assumed uncertainty boxes are not confidence statements."""
import nbformat as nbf


def interval_cells():
    md = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell
    return [
        md(r"""## 1 de noviembre: incertidumbre de las marginales
El certificado31 relajó la dependencia, pero todavía trataba las marginales como conocidas. Ahora estudiamos una **caja rectangular supuesta**: $r\in[r_-,r_+]$, $q_i\in[q_{i-},q_{i+}]$, $s\in[s_-,s_+]$. Son restricciones deterministas del escenario, **no intervalos de confianza**. No existe una muestra de asistencia ni una afirmación de cobertura95%. La meta original0,85 y el menú autorizado se conservan. Pregunta: ¿qué perturbaciones invalidan la elección puntual de B?

Probabilidades sin unidades por sesión; costos abstractos por opción del mismo par elegible. El rol R sigue teniendo la misma marginal en normal y shock. Eventos y supuestos estructurales de31 se mantienen: en normal basta R; en shock hacen falta R,B1,B2. Clase rectangular permite combinar todos los extremos y puede ser conservadora si hay restricciones entre parámetros."""),
        md(r"""### De la fórmula puntual a la envolvente de caja
De31, $L(r,q_1,q_2,s)=(1-s)r+s(r+q_1+q_2-2)_+$ y $U=(1-s)r+s\min(r,q_1,q_2)$.

**Paso1: marginales.** Ambas expresiones son no decrecientes en cada marginal. Para L, suma lineal de $r$ y parte positiva de una suma; para U, mínimo de funciones no decrecientes y término lineal. Por tanto el mínimo está en las marginales inferiores y el máximo en las superiores.

**Paso2: peso del shock.** Para marginales fijas, la pendiente de L respecto a $s$ es $(r+q_1+q_2-2)_+-r\le0$, porque $q_i\le1$; la de U es $\min(r,q_1,q_2)-r\le0$. Así, el mínimo usa$s_+$ y el máximo usa$s_-$.

$$L_{box}=(1-s_+)r_-+s_+(r_-+q_{1-}+q_{2-}-2)_+,$$
$$U_{box}=(1-s_-)r_++s_-\min(r_+,q_{1+},q_{2+}).$$

La caja es compacta y no vacía si los intervalos son válidos; las funciones son continuas, luego los extremos existen. Las esquinas pertenecen a la caja y las cotas31 son puntualmente alcanzables, por lo que la envolvente es sharp **para este evento y esta clase rectangular**. No es un resultado original. Caja puntual recupera31; ampliar una caja nunca mejora L ni disminuye U. Perdemos precisión y podemos pagar protección excesiva, conservando validez condicional si los valores verdaderos están dentro de la caja."""),
        code("from src.interval_role import ProbabilityInterval as PI, IntervalPlan, interval_bounds, select_interval\nfrom benchmarks.interval_run import load_config, lp_bounds\nicfg,iplans,irisk,ishock=load_config()\nidf=pd.DataFrame([{'plan':p.name,'cost':p.cost,**interval_bounds(p,irisk,ishock)} for p in iplans])\ndisplay(icfg['interval_semantics'])\ndisplay(idf.round(6))\nassert abs(idf.loc[1,'lower']-.8476)<1e-12\nassert select_interval(iplans,irisk,ishock,icfg['target']).name=='C'"),
        md(r"""### Alternativa independiente: LP con desigualdades
No fijamos las marginales en los extremos dentro del LP. Para cada una de las ocho masas $p_{abc}$ imponemos $p\ge0$, $\sum p=1$, y $r_-\le\sum a p\le r_+$, con restricciones análogas para B1/B2. El objetivo incluye ambos regímenes: $\sum[(1-s)a+s\mathbf{1}_{a=b=c=1}]p_{abc}$. En el mínimo usamos$s_+$; en el máximo$s_-$, justificados por monotonía. El coeficiente de R en normal hace que el LP también optimice esa marginal; no se añade por fuera un valor puntual incompatible.

Verifiquemos las masas y marginales del contraejemplo de B. La asignación de shock es una ley posible, no una frecuencia observada."""),
        code("ilower,imass,istates=lp_bounds(iplans[1],irisk,ishock)\niw=pd.DataFrame(istates,columns=['R','B1','B2'])\niw['mass']=imass\ndisplay(iw)\ndisplay(dict(zip(['r','q1','q2'],istates.T@imass)))\nassert abs(imass.sum()-1)<1e-10\nassert abs(ilower-.8476)<1e-10\nioracle=pd.read_csv('results/interval_oracle.csv')\nassert ioracle.max_error.max()<1e-10\nprint('Cajas de oráculo:',len(ioracle),'error máximo:',ioracle.max_error.max())"),
        md(r"""### Sensibilidad y decisión al mismo umbral
B tenía certificado puntual0,870. Su caja supuesta usa$r\in[0,94;0,96]$, $q_i\in[0,78;0,82]$, $s\in[0,19;0,21]$: el certificado cae a0,8476 y no cumple0,85. C tiene cota0,8896 y costo4 frente al costo3 de B. El baseline puntual y la caja tienen el mismo menú, costo, evento y meta; la diferencia es información de incertidumbre admitida, no superioridad predictiva.

La fracción de anchura $\alpha\in[0,1]$ genera cajas anidadas alrededor del punto, con semianchos $(0,01\alpha;0,02\alpha;0,02\alpha;0,01\alpha)$ para r,q1,q2,s. La figura enseña cuándo se pierde el certificado de B y cuánto cuesta garantizar la meta bajo el supuesto. No contiene barras de confianza."""),
        code("display(pd.read_csv('results/interval_plans.csv').round(6))\ndisplay(Image(filename='results/interval_role.png'))\nisummary=json.loads(Path('results/interval_summary.json').read_text())\ndisplay(isummary['timing_n100_median_seconds'])\nfor p in iplans:\n    rpoint=PI(.95,.95);spoint=PI(.2,.2)\n    qmid=(p.q1.lower+p.q1.upper)/2\n    ipoint=IntervalPlan(p.name,PI(qmid,qmid),PI(qmid,qmid),p.cost)\n    expected=joint_bounds(ReservePlan(p.name,qmid,qmid,p.cost))\n    assert abs(interval_bounds(ipoint,rpoint,spoint)['lower']-expected['lower'])<1e-12"),
        md(r"""### Interpretación, negativos y próximos hitos
**Continuar** como auditoría sintética si se aceptan caja y reglas del evento; **ajustar** de B a C cuando sea necesario certificar0,85 dentro de esa caja; **cerrar** la recomendación del menú si ninguna opción cumple, sin bajar el quórum para forzar éxito. Con caja puntual se recupera31; con todos presentes se obtiene1; meta0,97 sigue inviable en la caja actual. Intervalos más amplios pueden inducir conservadurismo innecesario.

Una garantía robusta es condicional a que las restricciones sean verdaderas. Sin procedimiento de estimación no significa95% de confianza, ni frecuencia real, causalidad o mejor calidad de decisiones. Si futuros intervalos fueran estimados, haría falta una cobertura **simultánea** y un contrato temporal de datos; marginales individuales95% no transfieren automáticamente una garantía conjunta95%.

Fórmula y LP coinciden en precisión; la fórmula especializada ahorra cómputo y el LP admite restricciones adicionales. Tiempos excluyen instalación e importación; memoria Python no incluye nativa HiGHS/RSS. Son cotas y optimización clásicas adaptadas al componente, no una contribución disciplinar original. Siguiente hito: contrato de datos y escenarios de restricciones conjuntas defendibles, manteniendo separación entre sensibilidad supuesta y validación empírica."""),
    ]
