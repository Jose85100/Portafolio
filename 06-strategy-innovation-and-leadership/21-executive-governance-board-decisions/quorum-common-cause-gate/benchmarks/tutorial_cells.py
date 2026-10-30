"""Teaching extension appended to the same cumulative Oct29 notebook."""
import nbformat as nbf


def md(text):
    # Placeholder avoids escape ambiguity when authoring LaTeX in source tooling.
    return nbf.v4.new_markdown_cell(text.replace('§',chr(92)))


def extension_cells():
    return [
        md('''# Iteración 30: investigar el supuesto pendiente del 29

## Pregunta de continuidad
El 29 se fijó asistencia 0,9 de cada reserva en todos los regímenes y se asumió independencia condicional. Su roadmap pidió que las reservas también sufran la disrupción. Hoy conservamos evento, miembros, quórum y rol obligatorio, pero permitimos marginales diferentes durante disrupción y dependencia arbitraria **entre dos reservas**.

Separamos las ablations: recuperar 29 (q=0,9), degradar marginales a 0,7 y después cambiar la distribución conjunta manteniendo esas marginales.

**Antes de calcular:** si ambas reservas asisten con probabilidad 70%, ¿sabemos la probabilidad de que estén las dos? Multiplicar 0,7 por 0,7 exige independencia. Intente construir una tabla 2×2 con esas mismas marginales y otro valor de la celda 11.'''),
        md('''## 1. Reducir el modelo original sin cambiar el evento
Sean $Z$ el régimen, $R$ la presencia del responsable de riesgo y $B_1,B_2$ las reservas. El evento sigue siendo
$$E=§{R=1,§ §text{asistentes}§ge3§}.$$
En normal, los tres miembros principales están presentes: solo falta $R$. En disrupción, los tres faltan y se necesitan simultáneamente $R,B_1,B_2$.

Escriba $s=P(Z=§text{disrupción})$ y $r=P(R=1§mid Z)$ constante. Se **mantiene** la independencia de $R$ respecto del par de reservas condicional al régimen. Por probabilidad total:
$$P(E)=(1-s)r+sr§,t=r[(1-s)+st],§qquad t=P(B_1=B_2=1§mid Z=§text{disrupción}).$$
El modelo 29 usaba $t=q_1q_2$. La propuesta sustituye ese supuesto puntual por todos los $t$ compatibles con las marginales, sin modificar el evento.'''),
        md('''## 2. Derivar las cotas desde la tabla de estados
Fije $q_1=P(B_1=1§mid Z)$ y $q_2=P(B_2=1§mid Z)$. Si $p_{11}=t$, las otras celdas son
$$p_{10}=q_1-t,§quad p_{01}=q_2-t,§quad p_{00}=1-q_1-q_2+t.$$
Suman uno y reproducen las marginales. La no negatividad implica
$$§max(0,q_1+q_2-1)§le t§le§min(q_1,q_2).$$
Son cotas Fréchet–Hoeffding clásicas, no una fórmula nueva. Son **sharp**: las cuatro celdas construyen una distribución válida en cada extremo. La disponibilidad es lineal creciente en $t$, por lo que
$$L=r[(1-s)+s§max(0,q_1+q_2-1)],§quad U=r[(1-s)+s§min(q_1,q_2)].$$
El oracle LP de los tests minimiza/maximiza $p_{11}$ sujeto a suma uno, marginales y no negatividad, sin usar esta fórmula cerrada.'''),
        nbf.v4.new_code_cell('''from src.reserve_ambiguity import ReservePlan, bounds, coupling, nominal_existing_engine
config30=json.loads(Path('config_dependence.json').read_text())
summary30=json.loads(Path('results/dependence_summary.json').read_text())
display(pd.read_csv('results/reserve_couplings.csv'))
p=ReservePlan('exercise',.7,.7,2)
b=bounds(p)
for key in ['lower_joint','independent_joint','upper_joint']:
    masses=coupling(p,b[key])
    assert abs(sum(masses)-1)<1e-12
    assert abs(masses[2]+masses[3]-.7)<1e-12
    assert abs(masses[1]+masses[3]-.7)<1e-12
display(b)'''),
        md('''## 3. Separar cambios de marginales y dependencia
- Recuperar 29: q=0,9, nominal 0,9139 y lower 0,912.
- Degradar solo marginales: q=0,7, nominal 0,8531.
- Mismas marginales 0,7, peor dependencia: 0,836, por debajo de meta 0,85.
- Mismas marginales 0,7, dependencia positiva perfecta: 0,893, **mayor** que independencia.

¿Por qué la última mejora? En el régimen crítico se requieren ambas reservas (AND); asistencia conjunta positiva ayuda. No toda correlación empeora disponibilidad. La ausencia común del grupo principal y la dependencia dentro del par son objetos distintos.'''),
        nbf.v4.new_code_cell('''display(pd.read_csv('results/dependence_plans.csv').round(6))
display(summary30['original29_q09_bounds'])
for row in config30['plans']:
    plan=ReservePlan(**row)
    assert abs(nominal_existing_engine(plan)-bounds(plan)['nominal_availability'])<1e-12
display(Image(filename='results/dependence.png'))'''),
        md('''## 4. Obtener una frontera de decisión
Para reservas simétricas $q_1=q_2=q$, defina
$$c=§frac{§tau/r-(1-s)}s.$$
Si $0<c§le1$, independencia exige $q^2§ge c$, mientras la garantía sharp exige $2q-1§ge c$:
$$q_{§mathrm{nom}}§ge§sqrt c,§qquad q_{§mathrm{rob}}§ge§frac{1+c}{2}.$$
Con $§tau=0,85$, $r=0,95$ y $s=0,2$: $q_{nom}=0,688247$ frente a $q_{rob}=0,736842$. Si $c§le0$, normal ya basta. Si $c>1$, ni reservas perfectas cubren la meta bajo estos supuestos.

El menú representa opciones hipotéticas, no probabilidades elegidas mágicamente: A(q=0,7,coste 2) pasa nominalmente; B(q=0,8,coste 3) es la mínima que cumple la cota robusta; C(q=0,9,coste 4) también cumple.'''),
        nbf.v4.new_code_cell('''display(summary30)
assert summary30['nominal_choice']['name']=='availability_A'
assert summary30['nominal_choice']['nominal_availability']>=.85>summary30['nominal_choice']['lower_availability']
assert summary30['robust_choice']['name']=='availability_B'
assert summary30['robust_choice']['lower_availability']>=.85
display(pd.read_csv('results/dependence_scaling.csv'))'''),
        md('''## 5. Qué aprendemos y qué queda pendiente
La contribución es una **adaptación operativa de cotas conocidas** a la herramienta 29, con baseline recuperado y menú auditable. No es una copula nueva, probabilidad calibrada o eficacia de gobierno demostrada.

La garantía cubre solamente dependencia entre dos reservas durante disrupción, con marginales y modelo del rol obligatorio fijos. No cubre correlación del responsable de riesgo con reservas, error de marginales, estatutos o calidad de decisiones. El conjunto amplio puede ser conservador: evidencia de dependencia positiva podría estrecharlo.

Antes de una aplicación: justificar elegibilidad, medir marginales durante incidentes e identificar causas compartidas. Consulte matriz_prior_art.md, RESEARCH_LOG.md y ROADMAP.md para clasificación, negativos y pruebas siguientes.''')
    ]
