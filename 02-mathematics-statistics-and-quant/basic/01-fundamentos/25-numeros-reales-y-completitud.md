# 25. Números reales, intervalos y completitud

**Pregunta:** ¿por qué necesitamos más números que las fracciones?  
**Objetivo:** distinguir racionales, reales, cotas y supremos. **Antes:** lecciones 1, 8 y 14.

## 1. Construir los conjuntos numéricos

Los naturales permiten contar; los enteros añaden cero y negativos; los racionales son cocientes a/b de enteros con b≠0. Los reales incluyen además irracionales como √2. Tenemos:
$$\mathbb N\subset\mathbb Z\subset\mathbb Q\subset\mathbb R.$$
Conviene declarar si cero pertenece a ℕ; ambas convenciones se usan. Ninguna altera las demostraciones si somos consistentes.

Un decimal periódico representa un racional. Si x=0.333…, entonces 10x−x=3 y x=1/3. La elipsis representa una expansión infinita con el patrón indicado; una pantalla finita nunca basta para establecer periodicidad.

## 2. Demostrar que √2 es irracional

Supón, para llegar a una contradicción, que √2=a/b, con a,b enteros positivos sin divisor común. Elevar al cuadrado:
$$a^2=2b^2.$$
Por tanto a² es par. Si a fuera impar, a=2k+1 y a²=2(2k²+2k)+1 sería impar; luego a debe ser par. Escribe a=2c:
$$4c^2=2b^2\Rightarrow b^2=2c^2.$$
El mismo argumento implica que b es par. Ambos tienen factor 2, contradiciendo que la fracción estaba reducida. Por ello no existe tal fracción.

El razonamiento no dice que no podamos aproximar √2 con racionales; dice que ninguna aproximación racional es exactamente √2.

## 3. Cota superior, máximo y supremo

Sea A=(0,1). Un número M es cota superior si x≤M para todo x∈A. Tanto 1 como 2 son cotas superiores, pero 1 es la menor. Se llama supremo:
$$\sup A=1.$$
No hay máximo, porque 1 no pertenece a A y para cualquier x<1 existe (x+1)/2 entre x y 1.

En B=[0,1], el supremo también es 1 y ahora sí es máximo. La distinción es pertenencia al conjunto, no una diferencia de tamaño.

## 4. Qué aporta la completitud de los reales

La propiedad de completitud establece que todo subconjunto no vacío de ℝ acotado superiormente tiene supremo en ℝ. Es una propiedad estructural de los reales, que aquí usamos como fundamento y no demostramos desde una construcción del sistema numérico.

Los racionales no la satisfacen dentro de sí mismos. El conjunto de racionales positivos q con q²<2 está acotado, pero no tiene supremo racional: su frontera real es √2.

De la completitud se deduce el teorema de convergencia monótona: una sucesión real creciente y acotada superiormente converge a su supremo. Para ver la idea, sea L=sup{aₙ}. Dado ε>0, algún a_N supera L−ε, pues de otro modo L−ε sería una cota superior menor. Para n≥N:
$$L-\varepsilon<a_N\le a_n\le L.$$
Así |aₙ−L|<ε. Esta es una demostración del teorema para sucesiones crecientes.

## 5. Un caso trabajado

aₙ=1−1/n, n≥1, es creciente porque:
$$a_{n+1}-a_n=\frac1n-\frac1{n+1}=\frac1{n(n+1)}>0.$$
Está acotada por 1 y converge a 1. Nunca alcanza ese límite. Para error menor que 0.01 necesitamos 1/n<0.01, es decir n>100; n=100 solo da igualdad.

## Ejercicios y soluciones

1. Supremo y máximo de [−2,3): supremo 3; no hay máximo.
2. Ínfimo y mínimo de (0,2]: ínfimo 0; no hay mínimo.
3. ¿Toda sucesión acotada converge? No: (−1)ⁿ está acotada y oscila.
4. En aₙ=1−1/n, ¿existe un mayor término? No: siempre hay uno siguiente más grande.

**Error frecuente:** confundir «se aproxima tanto como queramos» con «eventualmente se vuelve igual». Los límites no exigen alcanzar el valor.
