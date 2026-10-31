"""Oct31 teaching extension preserving all earlier notebook cells."""
import nbformat as nbf


def joint_cells():
    md = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell
    return [
        md(r"""## 31 octubre: ¿y si el rol obligatorio también depende de las reservas?
La pregunta central acumulativa es certificar disponibilidad, sin confundirla con calidad de gobierno. El30 relajamos solo la dependencia entre suplentes. Hoy contrastamos esa garantía contra la clase de todas las leyes conjuntas de $R,B_1,B_2$ con marginales conocidas. Son **cotas clásicas especializadas y auditoría de supuestos**, no nueva teoría de cópulas. La decisión original con meta0,85 se conserva; una frontera diseñada0,872 evidencia cuándo cambia. No es calibración empírica ni selección posterior presentada como confirmación.

### Notación, unidades y supuestos
$R,B_i\in\{0,1\}$ indican asistencia por sesión, $s\in[0,1]$ es peso de disrupción, $r=P(R=1\mid g)$ en ambos regímenes; $q_i=P(B_i=1\mid shock)$. Todos son adimensionales. Tres principales asisten en normal y ninguno en shock. Quórum fijo3 y presencia de Robligatoria. Por tanto $E=\{R=1\}$ en normal y $E=\{R=B_1=B_2=1\}$ en shock. Elegibilidad/autorización siguen supuestas. No datos de personas ni reglas jurídicas."""),
        md(r"""### Derivación: original → limitación → extensión
Original30: $L_{30}=r[1-s+s\max(0,q_1+q_2-1)]$, requiere $R\perp(B_1,B_2)\mid g$. Sin esa independencia no podemos multiplicar por$r$.

Sea $p_{abc}=P(R=a,B_1=b,B_2=c\mid shock)$. Las8masas cumplen $p\ge0$, $\sum p=1$, $\sum ap=r$, $\sum bp=q_1$, $\sum cp=q_2$. Minimizamos/maximizamos$p_{111}$; conjunto no vacío porque contiene producto independiente y compacto por simplex, así que existen extremos.

Por complemento y cota de unión: $P(RB_1B_2=1)=1-P(R=0\cup B_1=0\cup B_2=0)\ge r+q_1+q_2-2$; además es$\ge0$. La intersección está contenida en cada evento, de donde$p_{111}\le\min(r,q_1,q_2)$. Se alcanzan puntualmente ambos extremos al acomodar complementos disjuntos hasta cubrir el espacio, o eventos anidados para el máximo. No se afirma que la envolvente inferior sea una cópula multivariada global; solo que cada punto admite un testigo.

Por probabilidad total:
$$L_{31}=(1-s)r+s\max(0,r+q_1+q_2-2),\quad U_{31}=(1-s)r+s\min(r,q_1,q_2).$$
La clase30 es subconjunto de31, luego$L_{31}\le L_{30}$; la garantía se hace más conservadora. Se conserva monotonía en marginales, límites$[0,r]$ y recuperación30 si$r=1$; con$s=0$ambos dan$r$. Perdemos la garantía menos conservadora basada en independencia; no se infiere dependencia real. Un LP independiente de8variables verifica ambas cotas y guarda testigos factibles."""),
        code("from src.joint_role import joint_bounds, select_joint\nfrom src.reserve_ambiguity import ReservePlan, choose_plan\nfrom benchmarks.joint_role_run import oracle\njcfg=json.loads(Path('config_joint_role.json').read_text())\njplans=[ReservePlan(**p) for p in jcfg['plans']]\njrows=[{'name':p.name,'cost':p.cost,**joint_bounds(p)} for p in jplans]\ndisplay(pd.DataFrame(jrows).round(6))\nassert abs(jrows[1]['lower']-.87)<1e-12"),
        md(r"""### Construir un contraejemplo, no solo mostrar una cota
ParaB, $r=0,95$, $q_1=q_2=0,8$. El30 certificaba$0,874$; el31certifica$0,870$. La diferencia es$0,004$probabilidad por sesión. ¿Puede existir una ley que alcance ese valor? Revisamos masas, suma, marginales y objetivo del LP, sin usar la expresión cerrada para construirlo."""),
        code("witness,states=oracle(.95,.8,.8)\nwtable=pd.DataFrame(states,columns=['R','B1','B2'])\nwtable['mass']=witness.x\ndisplay(wtable)\nassert abs(sum(witness.x)-1)<1e-10\nassert max(abs(states.T@witness.x-[.95,.8,.8]))<1e-10\nassert abs(.8*.95+.2*witness.x[-1]-.87)<1e-10\ngrid=pd.read_csv('results/joint_role_oracle.csv')\nassert grid.max_error.max()<1e-10\nprint('125 combinaciones, 250 objetivos LP; error máximo:',grid.max_error.max())"),
        md(r"""### Decisión, sensibilidad y coste de robustez
Con meta0,85, B sigue siendo la opción robusta mínima: el aporte no obliga a cambiar toda decisión. Con meta diseñada0,872, Bya no certifica yC(costo4) reemplazaB(costo3). Elumbral fue elegido explícitamente entre0,870y0,874para estudiar frontera, no como evidencia de eficacia empresarial. Elmenú/costos/marginales y evento son iguales entre métodos. Un LP exacto yla fórmula son igualmente precisos; fórmula ahorra cómputo en este caso estructural, LP permite extensiones con restricciones adicionales.

Cuando$q_1+q_2>1$ y$r+q_1+q_2>2$, $L_{30}-L_{31}=s(1-r)(2-q_1-q_2)$. Fuera de ese régimen opera la parte positiva yla expresión no se extrapola. Con$r=1$ la brecha desaparece. La figura muestra mecanismo y frontera, no intervalos de confianza."""),
        code("display(pd.read_csv('results/joint_role_decisions.csv'))\nassert select_joint(jplans,.85).name=='B'\nassert choose_plan(jplans,.872)['name']=='B'\nassert select_joint(jplans,.872).name=='C'\ndisplay(Image(filename='results/joint_role.png'))\njs=json.loads(Path('results/joint_role_summary.json').read_text())\ndisplay(js['timings_n100_median_seconds'])"),
        md(r"""### Falsación, límites y hoja de ruta
Resultados negativos preservados: meta0,85no cambia; meta0,97es imposible porque$P(E)\le r=0,95$; si$r=1$la ampliación no añade protección. Cotas31pueden ser demasiado conservadoras si datos válidos descartan dependencias extremas. Ningún dato estima$r,q,s$ni demuestra que el peor caso ocurra. Tiempo incluye llamadas de cálculo tras warmup y excluye instalación/importación; tracemalloc no mide memoria nativaHiGHS ni RSS. No hay necesidad de semillas porque no usamosMonteCarlo.

Continuar como auditoría sintética y reunir evidencia de asistencias autorizada. Ajustar si el umbral cae en brecha30/31, cuantificando costo adicional. Cerrar la recomendación de menú si no alcanza meta; no bajar quórum. Siguiente hito: intervalos marginales con cobertura estadística, después restricciones empíricas de dependencia. Componente S2 sintético verificado localmente; no programa validado uoperacional. Fuentes ymatriz en referencias.bib/matriz_prior_art.md."""),
    ]
