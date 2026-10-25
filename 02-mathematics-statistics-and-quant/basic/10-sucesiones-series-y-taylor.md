# 10. Sucesiones, series y aproximaciones de Taylor

**Objetivo:** reconocer qué converge y qué error queda. Prerrequisitos: funciones y derivadas. [Notebook](notebooks/08-series-taylor-y-dinamica.ipynb).

## Una lista no es su suma

Una sucesión es una lista ordenada $(a_n)$. En $a_n=1/n$, sus términos se acercan a cero. Una serie suma términos: $\sum_{n=1}^{\infty}a_n$. Que $a_n\to0$ es necesario para convergencia de la serie, pero no suficiente: la serie armónica diverge.

Una forma de verlo es agrupar: $1/3+1/4\ge1/2$, $1/5+\cdots+1/8\ge1/2$, y cada bloque que duplica el número de términos aporta al menos 1/2. La suma crece sin límite.

## Serie geométrica y error

Si $S_n=1+r+\cdots+r^n$, restar $rS_n$ deja $(1-r)S_n=1-r^{n+1}$. Para r≠1:
$$S_n=(1-r^{n+1})/(1-r).$$
Si |r|<1, el término final desaparece al tomar el límite y la suma infinita es 1/(1-r). El error de truncamiento es $|r|^{n+1}/|1-r|$. Si r=1, cada término vale 1; si r=-1, las sumas oscilan. No convergen.

## Taylor con resto

Una aproximación de segundo orden de una función alrededor de a es
$$f(x)\approx f(a)+f'(a)(x-a)+\tfrac12f''(a)(x-a)^2.$$
Si la tercera derivada está acotada por M entre a y x, el error absoluto no supera $M|x-a|^3/6$. Para la exponencial centrada en cero y |x|≤0.1, se puede usar M=e^0.1.

## Ejercicios con solución

1. Suma infinita de 1+0.5+0.25+…: 2. El error tras exponentes 0 a n es $2^{-n}$.
2. ¿Cuántos términos hacen el error menor que 0.01? Necesitas n≥7, es decir ocho términos.
3. Aproxima e^0.1 con grado 2: 1.105. El valor exacto es aproximadamente 1.105170; la cota es aproximadamente 0.0001842.

**Límite:** convergencia de una sucesión, una serie y una aproximación local son preguntas diferentes.

