# 31. Autovalores, formas cuadráticas y matrices de covarianzas

**Pregunta:** ¿en qué direcciones una transformación solo estira, encoge o cambia el signo?  
**Objetivo:** calcular autovalores sencillos y entender positividad. **Antes:** matrices, determinantes y bases.

## 1. Definición

Un vector v≠0 es autovector de A si:
$$Av=\lambda v.$$
λ es su autovalor. El vector cero se excluye porque satisface esa igualdad para cualquier λ y no identifica una dirección.

Reordenar da (A−λI)v=0. Para una matriz cuadrada, existe una solución no nula cuando:
$$\det(A-\lambda I)=0.$$
Esta es la ecuación característica.

## 2. Calcular un ejemplo completo

Para:
$$A=\begin{pmatrix}2&1\\1&2\end{pmatrix},$$
$$\det(A-\lambda I)=(2-\lambda)^2-1=(\lambda-1)(\lambda-3).$$
Los autovalores son 3 y 1. Para λ=3, −v₁+v₂=0, así que un autovector es (1,1). Para λ=1, v₁+v₂=0 y podemos tomar (1,−1).

Normalizamos:
$$q_1=\frac1{\sqrt2}(1,1)^T,\quad q_2=\frac1{\sqrt2}(1,-1)^T.$$
Son ortogonales y de norma uno. Con Q=[q₁ q₂]:
$$Q^TQ=I,\qquad A=Q\begin{pmatrix}3&0\\0&1\end{pmatrix}Q^T.$$
Podemos verificar la igualdad multiplicando.

## 3. Teorema espectral y forma cuadrática

El teorema espectral asegura que toda matriz real simétrica admite una base ortonormal de autovectores reales. Aquí lo usamos como teorema, no damos su demostración general.

Para x=Qz:
$$x^TAx=z^T\Lambda z=\sum_i\lambda_i z_i^2.$$
Por tanto una matriz simétrica es semidefinida positiva si todos sus autovalores son no negativos, y definida positiva si todos son positivos. En el ejemplo:
$$x^TAx=3z_1^2+z_2^2>0\quad(x\ne0).$$
Esto permite clasificar la curvatura de una función cuadrática y decidir si tiene mínimo estricto.

## 4. Por qué una covarianza debe ser semidefinida positiva

Sea R un vector aleatorio con segundos momentos finitos y matriz de covarianzas Σ. Para cualquier peso w:
$$w^T\Sigma w=\operatorname{Var}(w^TR)\ge0.$$
Así Σ es simétrica y semidefinida positiva. Si un cálculo produce una varianza negativa apreciable, hay una inconsistencia numérica o de construcción.

Para una matriz 2×2 de varianzas a,b y covarianza c, la condición incluye a,b≥0 y c²≤ab. Con varianzas 0.04 y 0.09, la covarianza no puede superar en módulo √(0.04·0.09)=0.06.

## 5. Qué no cubre el ejemplo simétrico

Una matriz real no simétrica puede tener autovalores complejos o no tener suficientes autovectores para diagonalizarse. Para la matriz [[1,1],[0,1]], el único autovalor es 1, pero los autovectores son múltiplos de (1,0). No hay una base de dos autovectores.

Determinante positivo tampoco garantiza positividad definida: −I en dimensión dos tiene determinante 1 y forma cuadrática negativa para todo vector no nulo.

## Ejercicios y soluciones

1. Autovalores de diag(2,−1): 2 y −1; su forma es indefinida.
2. Para [[1,1],[1,1]], los autovalores son 2 y 0; es semidefinida positiva, no definida positiva.
3. ¿Una covarianza puede tener autovalor cero? Sí: existe una combinación lineal de varianza cero.
4. ¿Son únicos los autovectores? No: cualquier múltiplo no nulo conserva la dirección; con autovalores repetidos hay más libertad.

**Conexión:** en componentes principales, los autovalores describen varianza en direcciones ortogonales; escalar variables cambia la matriz y por tanto la interpretación.
