# Balance por masa: derivación y contrato

## Derivación: unidad de filas, no número de grupos
Sea $C_i$ la componente declarada $i$, $w_i=|C_i|\in\mathbb N$ su tamaño (filas), $N=\sum_{i=1}^K w_i$ (filas). La decisión $x_i\in\{0,1\}$ lleva toda $C_i$ a entrenamiento si $x_i=1$. Objetivo de fracción $r=p/q$ sin unidades, con $0<p<q$ enteros:
$$s=\sum_i w_i x_i,\qquad 0<s<N,\qquad J(x)=|s-rN|\quad[\text{filas}].$$
Multiplicar por $q>0$ preserva el mínimo:
$$\arg\min_x J(x)=\arg\min_x |q s-pN|.$$
El código `best` usa solo enteros; exporta `deviation_rows=abs(q*s-p*N)/q`. No hay tolerancia numérica para el objetivo. Empates numéricos eligen menor masa; un testigo se conserva por orden determinista, sin prometer mínimo lexicográfico entre subconjuntos.

Estados alcanzables tras $i$ componentes:
$$R_0=\{0\},\qquad R_i=R_{i-1}\cup\{s+w_i:s\in R_{i-1}\}.$$
Inducción: cualquier subconjunto excluye $i$ (primer conjunto) o lo incluye una sola vez (segundo); inversamente cada estado tiene testigo factible. `list(witnesses.items())` congela $R_{i-1}$ antes de actualizar: no reutiliza una componente. Minimizar sobre $R_K\setminus\{0,N\}$ da óptimo del objetivo finito, no teorema estadístico ni garantía de generalización.

Sin cortar componentes se conserva el invariante $a(u)=a(v)$ para todo par en una misma componente. No prueba que el grafo sea completo/verdadero. DP con testigos de tuplas: hasta $N+1$ estados y tuplas de longitud $K$; coste conservador $O(K^2N)$ tiempo y $O(KN)$ memoria (sin bits de enteros/strings), además de componentes/ordenación. Guardias2000filas y100componentes limitan alcance, no SLA ni prueba de escalabilidad.
