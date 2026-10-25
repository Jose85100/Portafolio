# 21. Mínimos cuadrados: derivación y geometría

**Objetivo:** unir regresión, álgebra lineal y optimización sin recurrir a una fórmula opaca.  
**Prerrequisitos:** matrices, derivadas y regresión inicial. **Pregunta guía:** ¿qué significa proyectar los datos sobre un modelo?

## 1. Formular el problema

Sean y∈ℝⁿ y X∈ℝⁿˣᵖ. Cada fila representa una observación y cada columna un regresor; si queremos intercepto, añadimos una columna de unos. Buscamos:
$$\min_{\beta\in\mathbb R^p}S(\beta),\qquad S=(y-X\beta)^T(y-X\beta).$$
El residual e=y−Xβ mide la parte que la predicción no reproduce.

Expandir el producto da:
$$S=y^Ty-2\beta^TX^Ty+\beta^TX^TX\beta.$$
Las dos expresiones cruzadas son escalares iguales; por eso se combinan en el factor 2.

## 2. Derivar las ecuaciones normales

El gradiente respecto de β es:
$$\nabla S=-2X^Ty+2X^TX\beta.$$
Igualarlo a cero:
$$X^TX\hat\beta=X^Ty.$$
Si las columnas de X son linealmente independientes, XᵀX es definida positiva, porque:
$$v^TX^TXv=\|Xv\|_2^2>0\quad(v\ne0).$$
La Hessiana 2XᵀX es definida positiva y el mínimo es global y único. Simbólicamente:
$$\hat\beta=(X^TX)^{-1}X^Ty.$$
Esto explica la solución, pero no recomienda formar la inversa en una implementación: QR o SVD suelen ser opciones numéricas preferibles.

Si hay columnas dependientes, los coeficientes pueden no ser únicos. Aun así, la predicción óptima Xβ̂ es única como proyección sobre el espacio columna.

## 3. Por qué los residuos son ortogonales

Las ecuaciones normales implican:
$$X^T(y-X\hat\beta)=X^Te=0.$$
Así, e es perpendicular a cada columna de X y a toda combinación de ellas. La predicción ŷ=Xβ̂ es la proyección ortogonal de y sobre el espacio que el modelo puede representar.

Para cualquier otro β:
$$y-X\beta=e+X(\hat\beta-\beta).$$
Los dos términos son ortogonales, de modo que Pitágoras da:
$$
\|y-X\beta\|^2=\|e\|^2+\|X(\hat\beta-\beta)\|^2\ge\|e\|^2.
$$
Esta es una segunda demostración de optimalidad.

## 4. Ejemplo trabajado sin software

Con x=(1,2,3) e y=(2,3,5):
$$
X=\begin{pmatrix}1&1\\1&2\\1&3\end{pmatrix},\quad
X^TX=\begin{pmatrix}3&6\\6&14\end{pmatrix},\quad
X^Ty=\begin{pmatrix}10\\23\end{pmatrix}.
$$
Las ecuaciones son 3a+6b=10 y 6a+14b=23. Restar dos veces la primera de la segunda da 2b=3: b=3/2. Sustituyendo, a=1/3.

Las predicciones son (11/6,10/3,29/6), y los residuos:
$$e=(1/6,-1/3,1/6).$$
Comprueba:
$$\sum e_i=0,\qquad\sum x_ie_i=0,\qquad S=1/6.$$
Las dos primeras identidades son consecuencias del ajuste, no pruebas externas de calidad predictiva.

## 5. Ajuste, estadística y causalidad son niveles distintos

La solución algebraica existe sin suponer normalidad. Para interpretar β como una relación poblacional y estudiar propiedades estadísticas, hacen falta supuestos adicionales. Una condición típica de exogeneidad es E[ε|X]=0, junto con requisitos de rango y momentos.

Normalidad no es requisito para calcular OLS. Y obtener un residuo ortogonal a X en la muestra no demuestra exogeneidad: esa ortogonalidad está impuesta por el algoritmo.

## Ejercicios con solución

1. Si añades una segunda copia de la columna x, ¿los coeficientes son únicos? No: puedes repartir su efecto entre ambas columnas sin cambiar la predicción.
2. Si el modelo tiene solo intercepto, las ecuaciones normales dan n·a=Σyᵢ, es decir a=ȳ.
3. ¿Sin intercepto los residuos siempre suman cero? No: falta la columna de unos que impone esa condición.
4. ¿Menor error de entrenamiento garantiza mejor predicción futura? No: necesita evaluación fuera de muestra y un diseño compatible con el uso previsto.

**Conexión práctica:** [notebook de regresión](notebooks/07-regresion-y-residuos.ipynb). La derivación explica sus comprobaciones de ecuaciones normales.
