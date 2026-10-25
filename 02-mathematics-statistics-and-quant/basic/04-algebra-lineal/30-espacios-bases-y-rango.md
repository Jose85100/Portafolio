# 30. Espacios vectoriales, bases y rango

**Pregunta:** ¿cuánta información independiente contiene una matriz?  
**Objetivo:** construir bases, interpretar rango y relacionar soluciones con grados de libertad. **Antes:** vectores y sistemas lineales.

## 1. Combinaciones y espacios generados

Dados vectores v₁,…,vₖ, una combinación lineal es a₁v₁+…+aₖvₖ con coeficientes reales. Su conjunto de combinaciones es el espacio generado o span.

Los vectores (1,0) y (0,1) generan ℝ²: cualquier (x,y)=x(1,0)+y(0,1). En cambio, (1,2) y (2,4) solo generan una recta porque el segundo es múltiplo del primero.

Un subespacio debe contener cero y ser cerrado bajo sumas y multiplicación por escalares. La recta x+y=1 no es subespacio: no contiene el origen. La recta x+y=0 sí lo es.

## 2. Independencia y base

Una familia es linealmente independiente si:
$$a_1v_1+\cdots+a_kv_k=0\Rightarrow a_1=\cdots=a_k=0.$$
Una base es una familia independiente que genera el espacio. Cada vector tiene coordenadas únicas en esa base: si hubiera dos representaciones, restarlas produciría una combinación nula con coeficientes no todos cero.

Para v₁=(1,1), v₂=(1,−1):
$$(x,y)=\frac{x+y}{2}v_1+\frac{x-y}{2}v_2.$$
Así (3,1) tiene coordenadas (2,1) en esa base, aunque sus coordenadas estándar sean (3,1). El vector no cambió; cambió su descripción.

## 3. Núcleo e imagen de una matriz

Para A∈ℝᵐˣⁿ:
$$\ker A=\{x:Ax=0\},\qquad\operatorname{im}A=\{Ax:x\in\mathbb R^n\}.$$
El rango es la dimensión de la imagen; cuenta columnas independientes. El teorema rango–nulidad establece:
$$\operatorname{rango}(A)+\dim(\ker A)=n.$$
La idea de su demostración es tomar una base del núcleo y completarla a una base del dominio: las imágenes de los vectores añadidos forman una base de la imagen.

## 4. Ejemplo desarrollado

Sea:
$$A=\begin{pmatrix}1&2&3\\0&1&1\end{pmatrix}.$$
Su tercera columna es la suma de las dos primeras. Estas son independientes, así que rango(A)=2.

Para hallar el núcleo:
$$x_1+2x_2+3x_3=0,\quad x_2+x_3=0.$$
Toma x₃=t; entonces x₂=−t y x₁=−t. Por tanto:
$$\ker A=\{t(-1,-1,1):t\in\mathbb R\}.$$
Su dimensión es uno y 2+1=3, como predice rango–nulidad.

Para Ax=(4,1)ᵀ:
$$x_2=1-t,\quad x_1=2-t,\quad x_3=t.$$
Todas las soluciones son una particular (2,1,0) más un vector del núcleo. Distintos parámetros producen el mismo resultado observado.

## 5. Identificación y redundancia

Si dos columnas de una matriz de regresión son idénticas, solo la suma de sus coeficientes puede afectar la predicción; no se pueden identificar ambos por separado. Más filas no elimina una dependencia exacta entre columnas.

La dependencia casi exacta no reduce necesariamente el rango matemático, pero puede generar mala condición numérica. En cálculos con tolerancia, el «rango numérico» depende de escala y umbral.

## Ejercicios y soluciones

1. ¿(1,0),(0,1),(1,1) son independientes en ℝ²? No: el tercero es la suma de los anteriores.
2. Para A=[1 1], el núcleo es {(t,−t)} y el rango es uno.
3. ¿Un sistema con núcleo no trivial puede tener solución única? Si tiene una solución, no: sumar cualquier vector no nulo del núcleo produce otra.
4. ¿Una base de ℝ³ puede contener cuatro vectores? No: toda familia de cuatro vectores en ℝ³ es dependiente.

**Aplicación:** reducir variables redundantes exige comprender su significado; una relación algebraica exacta puede reflejar una identidad contable, no un problema de datos.
