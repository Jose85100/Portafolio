# 22. Ley de los grandes números y teorema central del límite

**Objetivo:** distinguir convergencia de un promedio y aproximación de su distribución.  
**Prerrequisitos:** esperanza, varianza y muestreo. **Pregunta guía:** ¿qué mejora exactamente cuando aumenta el tamaño muestral?

## 1. Derivar la varianza de una media

Sean X₁,…,Xₙ IID con media μ y varianza finita σ². Por linealidad:
$$E[\bar X_n]=\frac1n\sum_iE[X_i]=\mu.$$
Por independencia, las covarianzas cruzadas son cero:
$$\operatorname{Var}(\bar X_n)=\frac1{n^2}\sum_i\sigma^2=\frac{\sigma^2}{n}.$$
La desviación estándar de la media es σ/√n. Para reducirla a la mitad, hacen falta cuatro veces más observaciones; duplicar n solo la divide por √2.

## 2. Una demostración de convergencia con Chebyshev

Para una variable Z con varianza finita:
$$P(|Z-E[Z]|\ge\varepsilon)\le\frac{\operatorname{Var}(Z)}{\varepsilon^2}.$$
La desigualdad se obtiene porque, en el evento |Z−E[Z]|≥ε, el cuadrado de esa diferencia es al menos ε². Por tanto su esperanza no puede ser menor que ε² multiplicado por la probabilidad del evento.

Aplicada al promedio:
$$P(|\bar X_n-\mu|\ge\varepsilon)\le\frac{\sigma^2}{n\varepsilon^2}\to0.$$
Esto prueba una versión de la ley débil de los grandes números bajo los supuestos indicados. No asegura una reducción monotónica del error a medida que observamos cada dato nuevo.

**Ejemplo:** para Bernoulli con p=0.2, σ²=0.16. Si queremos que la cota de probabilidad de error ≥0.05 sea como máximo 0.05:
$$\frac{0.16}{n(0.05)^2}\le0.05\Rightarrow n\ge1280.$$
Es una garantía conservadora, no el tamaño mínimo exacto necesario.

## 3. Qué añade el límite central

Bajo las mismas condiciones IID, con 0<σ²<∞:
$$\frac{\sqrt n(\bar X_n-\mu)}{\sigma}\xrightarrow{d}N(0,1).$$
La media se concentra cerca de μ, pero sus errores, reescalados por √n, tienen una distribución límite no degenerada. Para valores fijos a<b:
$$P\left(a\le\frac{\sqrt n(\bar X_n-\mu)}{\sigma}\le b\right)\to\Phi(b)-\Phi(a).$$

El teorema no dice que los datos originales se vuelvan normales. Tampoco garantiza que n=30 sea suficiente: asimetría, colas y eventos raros afectan la calidad de la aproximación.

## 4. Dependencia: volver a la fórmula general

Sin independencia:
$$
\operatorname{Var}(\bar X_n)=\frac1{n^2}
\left[\sum_i\operatorname{Var}(X_i)+2\sum_{i<j}\operatorname{Cov}(X_i,X_j)\right].
$$
Correlaciones positivas pueden aumentar mucho la incertidumbre. En el caso extremo Xᵢ=Z para todos los i, la media siempre es Z; repetir el mismo dato no aporta información nueva y su varianza no disminuye.

Con varianza infinita, la demostración de Chebyshev anterior y el límite central clásico no se aplican. Eso no permite concluir automáticamente que toda ley de grandes números falle: existen resultados con otras hipótesis.

## Ejercicios y soluciones

1. Si σ=12 y n=36, el error estándar es 2.
2. Para error estándar 1 con la misma σ, se requiere n=144.
3. ¿La media puede alejarse de μ al añadir una observación? Sí: convergencia probabilística no implica mejora en cada paso.
4. ¿Mil copias del mismo registro equivalen a mil observaciones IID? No; comparten toda su variación.

**Conexión:** [notebook de cobertura](notebooks/06-muestreo-e-inferencia.ipynb). La simulación ilustra repeticiones finitas; la demostración establece el comportamiento asintótico bajo supuestos.
