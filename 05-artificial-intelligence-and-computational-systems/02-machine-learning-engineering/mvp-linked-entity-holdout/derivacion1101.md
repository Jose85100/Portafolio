# Adjudicación parcial: cotas de exposición alcanzables

## Original y limitación

El auditor31 exige una partición verdadera completa T de V y calcula $E(T,A)=\sum_{t\in T}|t|1\{t\cap A\ne\emptyset,t\cap A^c\ne\emptyset\}$. E cuenta filas pertenecientes a una identidad repartida; no probabilidades ni pares ni impacto predictivo. Rechazar adjudicación incompleta es honesto pero no aprovecha información parcial. Fuentes conceptuales: identificación parcial (Tamer2010), evaluación de entity resolution (Binette/Steorts2022) y garantía condicional31, sin atribuir esta fórmula a esas fuentes.

## Supuestos, dominio e identificación

V es universo finito de n IDs, cada uno asignado a train o test. K⊆V posee **equivalencia completa y correcta entre todos los adjudicados**, incluidas diferencias entre clases; no basta una lista de enlaces positivos faltantes. U=V\K son IDs sin adjudicar. Una completación puede asignar cada desconocido a una clase conocida o a una nueva, pero nunca fusionar dos clases conocidas distintas. El grafo observado O sirve solo para diagnosticar cortes declarados, **no restringe la verdad**. No hay probabilidades, muestreo aleatorio obligatorio ni supuesto missing-at-random. La identidad real debe ser alguna completación admitida; de otro modo no hay garantía. No identificamos E puntual salvo que L=H.

Sean M clases conocidas mixtas, P clases puras train con tamaños $a_1\ge\cdots\ge a_p$, Q clases puras test con tamaños $b_1\ge\cdots\ge b_q$; u_train/u_test son desconocidos en cada lado y u su suma. Unidades: todos son filas excepto p/q números de clases. Si ambos lados globales tienen filas:

$$L=\sum_{m\in M}|m|,$$
$$H=L+u+\sum_{i=1}^{\min(p,u_{test})}a_i+\sum_{j=1}^{\min(q,u_{train})}b_j.$$

Si todas las filas están en un solo lado, L=H=0. Este caso no constituye un holdout útil, aunque matemáticamente ninguna identidad cruza lados.

## Derivación paso a paso

1. Una clase mixta conocida sigue mixta en cualquier completación: cada una de sus filas contribuye a E. Esto fuerza L. Se alcanza L dejando desconocidos singleton y sin fusionar clases conocidas; por eso no se suman los desconocidos a la cota inferior.
2. Una clase pura train solo puede volverse mixta si recibe al menos un desconocido test: otra clase conocida no puede fusionarse con ella. Cada desconocido pertenece a una sola clase, por tanto como máximo u_test clases puras train se exponen. Para maximizar el número de **filas conocidas** expuestas se eligen las mayores a_i. Simétricamente se eligen las mayores u_train clases puras test.
3. Cada desconocido aporta como máximo una fila expuesta. Sumar u da una cota superior H. Sus términos son subconjuntos disjuntos de filas, luego H≤n.
4. Alcanzabilidad: asignar un desconocido del lado opuesto a cada clase pura seleccionada. Esto usa presupuestos separados u_test y u_train. Si ya hay clase mixta, cualquier desconocido sobrante puede unirse a ella. Si no había mixta pero se seleccionó alguna pura, esa clase ya es mixta y absorbe sobrantes. Si no hay ninguna clase seleccionada/mixta y u>0, el único caso con ambos lados globales presentes es que hay desconocidos de ambos lados: formar una nueva clase mixta con todos ellos. Si u=0, H=L. Así existe completación con E=H en todos los casos admitidos.
5. Por1–4, L y H son extremos exactos, no intervalos de confianza ni estimaciones de prevalencia. No afirmamos que cada entero entre ambos extremos sea alcanzable. El oráculo exhaustivo enumera particiones distintas y comprueba los extremos para n≤6, además de la deducción anterior; la prueba numérica no sustituye sus supuestos.

## Propiedades y pérdidas

Con K=V, u=0 y L=H=E del auditor31. Con K vacío y ambos lados presentes, [L,H]=[0,n]: abstención informativa. Adjudicar más filas coherentemente restringe las completaciones, por tanto L no disminuye ni H aumenta, aunque el aumento de cobertura no garantiza anchura pequeña. Invariancia a renombrar IDs/clases y al orden de entradas; enteros exactos sin overflow de punto flotante, memoria finita. Coste O(n log n+L_id), L_id incidencias de identidad, por components/sort; memoria O(n+L_id). No enumeramos completaciones en producción.

La decisión es detected si L>0, conditional-zero si H=0, abstain en otro caso; detected no significa E identificado puntualmente. El término conditional-zero expresa dependencia estricta de la adjudicación asumida correcta. Si dos filas adjudicadas distintas son en realidad la misma persona, puede dar [0,0] y E_real=2: negativo explícito fuera del dominio. Es imposible detectar ese error solo con entradas suministradas. No certificamos independencia real con cobertura parcial ni temporalidad; fechas y origen de adjudicación quedan pendientes.
