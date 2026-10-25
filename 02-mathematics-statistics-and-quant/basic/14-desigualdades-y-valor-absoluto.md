# 14. Valor absoluto y desigualdades: razonar con cotas

**Objetivo:** resolver desigualdades sin perder casos y justificar cotas que luego aparecen en error numérico y riesgo.  
**Prerrequisitos:** lecciones 1 y 8. **Pregunta guía:** ¿cómo demostrar que un error es pequeño sin calcularlo exactamente?

## 1. El valor absoluto mide distancia

Para un real x:
$$
|x|=\begin{cases}x,&x\ge0,\\-x,&x<0.\end{cases}
$$
No significa «borrar el signo» de cualquier expresión: primero hay que determinar el signo de la expresión completa. Por ejemplo, |2−5|=3, mientras |2|−|5|=−3.

La distancia entre a y b es |a−b|. Por eso, para ε>0:
$$|x-a|<\varepsilon\iff a-\varepsilon<x<a+\varepsilon.$$
Restar a centra el intervalo en cero; el valor absoluto mide cuánto nos alejamos sin importar la dirección.

**Ejemplo.** |2x−3|≤5 equivale a −5≤2x−3≤5. Sumar 3 a los tres miembros y dividir por 2 produce −1≤x≤4. Comprobar ambos extremos ayuda a verificar los signos.

## 2. Una desigualdad racional requiere casos

Resolvamos:
$$\frac{x-1}{x+2}\ge0.$$
Primero excluimos x=−2. Los puntos donde puede cambiar el signo son −2 y 1.

| Intervalo | Signo de x−1 | Signo de x+2 | Cociente |
|---|---|---|---|
| x<−2 | − | − | + |
| −2<x<1 | − | + | − |
| x>1 | + | + | + |

El numerador se anula en 1, que sí se admite. Resultado:
$$(-\infty,-2)\cup[1,\infty).$$
Multiplicar directamente por x+2 sin conocer su signo habría sido un error: si es negativo, la desigualdad se invierte.

## 3. Demostrar la desigualdad triangular

Queremos justificar |a+b|≤|a|+|b|. Observa:
$$
(|a|+|b|)^2-(a+b)^2=2(|a||b|-ab)\ge0.
$$
La última desigualdad se cumple porque |a||b|=|ab|≥ab. Como los dos lados comparados son no negativos, tomar raíces conserva el orden.

La interpretación es geométrica: ir directamente de un punto a otro no es más largo que hacer un desvío intermedio.

Si una aproximación introduce errores e₁ y e₂:
$$|e_1+e_2|\le|e_1|+|e_2|.$$
Si |e₁|≤0.02 y |e₂|≤0.03, el error total está acotado por 0.05. Puede ser menor por cancelación, pero no podemos garantizarla solo con estas cotas.

## 4. De cuadrados a una desigualdad útil

Como (a−b)²≥0:
$$a^2-2ab+b^2\ge0\Rightarrow 2ab\le a^2+b^2.$$
Si a,b≥0, esto también lleva a la relación entre media aritmética y geométrica:
$$\sqrt{ab}\le\frac{a+b}{2},$$
pues (√a−√b)²≥0. La igualdad ocurre exactamente cuando a=b.

Para dos insumos positivos con suma fija s, su producto no supera s²/4; el máximo se alcanza al repartir por igual. Es una optimización que puede resolverse sin derivadas.

## Ejercicios antes de mirar

1. Resuelve |x+1|<3.
2. Resuelve (x+1)/(x−2)<0.
3. Si |a−b|≤0.1 y |b−c|≤0.2, acota |a−c|.
4. Maximiza xy con x,y≥0 y x+y=10.

## Soluciones desarrolladas

1. −3<x+1<3; restando 1: −4<x<2.
2. Los puntos críticos son −1 y 2. Los signos difieren únicamente en (−1,2); no se incluyen extremos.
3. Escribe a−c=(a−b)+(b−c). La triangular da |a−c|≤0.3.
4. xy≤(x+y)²/4=25; igualdad en x=y=5.

**Límite de la conclusión:** una cota es una garantía superior, no una predicción del error observado. Para desigualdades estrictas, revisa cuidadosamente qué extremos se incluyen.

**Conexión:** [integración numérica](notebooks/04-integracion-y-convergencia.ipynb) y [Taylor](10-sucesiones-series-y-taylor.md).
