# 9. Combinatoria: contar sin duplicar

**Objetivo:** decidir si importa el orden y si se permite repetir. Continúa con el notebook de Bayes y distribuciones.

## Regla del producto

Si una selección tiene m opciones y, para cada una, otra tiene n, hay mn pares posibles. Un código de dos dígitos permite 100 secuencias si admite ceros iniciales y repetición, pero solo 90 si no admite repetir dígitos: 10 opciones y luego 9. Las restricciones cambian el conteo.

El factorial $n!=n(n-1)\cdots1$ cuenta ordenaciones de n objetos distintos; $0!=1$ permite que las identidades funcionen también para la selección vacía.

## Orden frente a selección

Elegir presidente y secretario entre cinco personas da $5\cdot4=20$: los cargos distinguen el orden. Elegir un comité de dos da $\binom52=5!/(2!3!)=10$. Cada pareja apareció dos veces al ordenar; dividimos por 2!.

En general, seleccionar k objetos distintos sin reemplazo y sin orden da
$$\binom nk=\frac{n!}{k!(n-k)!},\qquad 0\le k\le n.$$
No uses esta fórmula si los objetos se repiten o si el orden es parte del resultado.

## Conexión con probabilidad

En cuatro ensayos Bernoulli independientes con probabilidad p, exactamente dos éxitos pueden ocupar $\binom42=6$ patrones. Cada patrón tiene probabilidad $p^2(1-p)^2$, así que la probabilidad total es $6p^2(1-p)^2$. La combinación cuenta posiciones; la independencia justifica multiplicar probabilidades. No son el mismo supuesto.

## Ejercicios con solución

1. ¿Cuántas carteras de tres nombres distintos entre diez? Sin pesos ni orden: $\binom{10}3=120$.
2. ¿Cuántas secuencias de tres nombres distintos entre diez? $10\cdot9\cdot8=720$.
3. ¿Probabilidad de exactamente dos caras en cuatro monedas justas independientes? $6/16=0.375$.
4. ¿Cuenta el comité de tres como seis resultados distintos? No: sus $3!=6$ ordenaciones representan el mismo comité.

**Pregunta de control:** antes de calcular, describe qué dos resultados considerarías diferentes. Esa decisión determina la fórmula.

