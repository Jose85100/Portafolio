# Dependencia conjunta del rol obligatorio y dos reservas

Unidades: asistencia binaria por sesión; probabilidades adimensionales; costo abstracto por opción del mismo par elegible. $s$ peso de disrupción. $r=P(R=1\mid g)$ igual en ambos regímenes. $q_i=P(B_i=1\mid shock)$. Quórum fijo3 yR obligatorio, tres principales presentes normal y ausentes shock. No aprobación ni quórum legal.

Original30, derivado de independencia condicional del rol respecto al par:
$$L_{30}=r[1-s+s\max(0,q_1+q_2-1)].$$
Limitación: dependencia del rol aún excluida. Ampliamos el conjunto factible a todas las8masas $p_{abc}\ge0$, $\sum p=1$, $\sum ap=r$, $\sum bp=q_1$, $\sum cp=q_2$. Producto independiente asegura existencia; simplex cerrado acotado y objetivo lineal aseguran extremos alcanzados.

Evento en normal esR, en shock es $R\cap B_1\cap B_2$. No multiplicar marginales sin independencia. Por complemento de unión:
$$p_{111}=1-P(R^c\cup B_1^c\cup B_2^c)\ge1-[(1-r)+(1-q_1)+(1-q_2)]=r+q_1+q_2-2.$$
También $p_{111}\ge0$ y, por inclusión, $p_{111}\le\min(r,q_1,q_2)$. Ambas cotas son puntualmente sharp: eventos anidados dan cota superior; complementos con máxima unión dan inferior. Si suma de complementos≤1 se acomodan disjuntos; si supera1 cubren todo elespacio con solapamientos permitidos. No se sostiene que envolvente inferior sea una cópula global3D. LP8estados entrega testigos con marginales exactas para cada caso de benchmark.

Probabilidad total da:
$$L_{31}=(1-s)r+s\max(0,r+q_1+q_2-2),\quad U_{31}=(1-s)r+s\min(r,q_1,q_2).$$
Conservamos monotonía en marginales y $0\le L\le U\le r$, recuperación30 si$r=1$ o$s=0$. Perdemos garantía menos conservadora basada en independencia. Inclusión de conjuntos factibles implica $L_{31}\le L_{30}\le N\le U_{31}$, donde$N=r[1-s+sq_1q_2]$. En región $q_1+q_2>1$, $r+q_1+q_2>2$:
$$L_{30}-L_{31}=s(1-r)(2-q_1-q_2).$$
Fórmula por tramos, no extrapolar fuera de esa región. Condiciones: $r,q_1,q_2,s\in[0,1]$, marginales conocidas por régimen, eventos estructurales deterministas de los tres principales. Se evalúa precisión numérica tolerancia1e-10, no nuevo teorema. Fuente de cotas clásicas Nelsen2006; implementación LPdocumentada SciPyHiGHS. Adaptación de ingeniería y auditoría de supuestos del repositorio, no innovación disciplinar original.

Decisión: minimizar costo sobre menú sujeto a$L_{31}\ge\tau$. Umbral original0,85se conserva;0,872es benchmark diseñado explícitamente enbrechaB, no evidencia empírica. Continuar herramienta sintética, ajustar recomendación si umbral enbrecha, cerrar menú si ninguna opción cumple. No relajar quórum para fabricar factibilidad.
