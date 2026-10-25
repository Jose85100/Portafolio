# 3. Álgebra lineal: vectores, matrices y sistemas

**Objetivo:** interpretar combinaciones lineales y resolver un sistema sin tratar la matriz como una caja negra.

## Vectores y producto interno

Un vector reúne cantidades en un orden definido. Si $w=(0.6,0.4)$ contiene pesos y $r=(0.05,-0.02)$ rendimientos, el rendimiento agregado es
$$w^Tr=0.6(0.05)+0.4(-0.02)=0.022.$$
El resultado es 2.2%. No sumes coordenadas que representan unidades incompatibles. La norma $\|v\|_2=\sqrt{v^Tv}$ mide longitud; $\|(3,4)\|_2=5$. Producto interno cero indica ortogonalidad, no independencia estadística.

## Resolver por eliminación

Considera $x+y=3$ y $2x-y=0$. Sumar ecuaciones elimina $y$: $3x=3$, entonces $x=1$ y $y=2$.

La notación matricial es
$$
\begin{pmatrix}1&1\\2&-1\end{pmatrix}
\begin{pmatrix}x\\y\end{pmatrix}
=
\begin{pmatrix}3\\0\end{pmatrix}.
$$
Cada fila es una ecuación; cada columna describe cómo una incógnita afecta todas las ecuaciones. El producto se calcula multiplicando fila por columna. En general $AB\ne BA$, y las dimensiones deben ser compatibles.

El determinante de una matriz $2\times2$ es $ad-bc$. Aquí vale $-3$, distinto de cero: existe solución única. Si la segunda ecuación fuera $2x+2y=6$, sería redundante; habría infinitas soluciones. Si fuera $2x+2y=7$, sería incompatible. Determinante cero no significa automáticamente «ninguna solución».

## Varianza de una combinación

Con matriz de covarianzas
$$\Sigma=\begin{pmatrix}0.04&0.01\\0.01&0.09\end{pmatrix},$$
la varianza de $w^Tr$ es $w^T\Sigma w$. Para $w=(0.6,0.4)$:
$$0.6^2(0.04)+2(0.6)(0.4)(0.01)+0.4^2(0.09)=0.0336.$$
La desviación estándar es $\sqrt{0.0336}\approx0.1833$. El término cruzado importa. Este cálculo supone covarianzas y rendimientos medidos con la misma periodicidad.

## Ejercicios y soluciones

1. Resuelve $x+y=5$, $x-y=1$. Al sumar: $2x=6$, así que $x=3$, $y=2$.
2. ¿Son ortogonales $(1,2)$ y $(2,-1)$? Sí: $2-2=0$.
3. ¿Tiene inversa $\begin{pmatrix}1&2\\2&4\end{pmatrix}$? No: determinante cero; columnas dependientes.
4. ¿Por qué no resolver siempre con una inversa explícita? Un algoritmo de resolución evita trabajo innecesario y suele tener mejores propiedades numéricas. Además, matrices casi singulares amplifican pequeños errores.

**Para dibujar:** representa las rectas del sistema y observa que resolver significa localizar su intersección. Luego cambia una ecuación hasta que sean paralelas.
