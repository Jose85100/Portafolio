# 23. Convexidad y desigualdad de Jensen

**Objetivo:** reconocer problemas con mínimo global y entender por qué transformar un promedio no equivale a promediar una transformación.  
**Prerrequisitos:** funciones, derivadas y esperanza. **Pregunta guía:** ¿cómo influye la curvatura en el efecto de la dispersión?

## 1. Definición geométrica

En un dominio convexo, f es convexa si para x,y del dominio y 0≤t≤1:
$$f(tx+(1-t)y)\le tf(x)+(1-t)f(y).$$
El lado izquierdo evalúa el punto intermedio; el derecho interpola alturas. La gráfica queda por debajo de sus cuerdas. Convexa no significa creciente: x² es convexa en todos los reales y decrece para x<0.

La desigualdad es estricta para x≠y y 0<t<1 si f es estrictamente convexa.

## 2. Derivar el criterio de la tangente

Para f diferenciable y convexa:
$$f(y)\ge f(x)+f'(x)(y-x).$$
Una forma de obtenerlo es aplicar convexidad a x+t(y−x):
$$\frac{f(x+t(y-x))-f(x)}{t}\le f(y)-f(x).$$
Al tomar t→0⁺, el lado izquierdo tiende a f'(x)(y−x).

Si f'(x*)=0, la desigualdad da f(y)≥f(x*) para cualquier y del dominio: x* es mínimo global. La convexidad convierte una condición local en una garantía global. En varias dimensiones se reemplaza f'(x)(y−x) por ∇f(x)ᵀ(y−x).

Para funciones dos veces diferenciables en un intervalo, f''≥0 caracteriza convexidad. Si f''>0 en todo el intervalo, hay convexidad estricta. La recíproca estricta no es necesaria: x⁴ es estrictamente convexa aunque su segunda derivada se anule en cero.

## 3. Jensen para dos valores y para una distribución

La definición ya demuestra que:
$$f(E[X])\le E[f(X)]$$
cuando X solo toma dos valores con probabilidades t y 1−t.

Para una variable general con media μ y una función convexa diferenciable en μ, la tangente da:
$$f(X)\ge f(\mu)+f'(\mu)(X-\mu).$$
Tomar esperanza elimina el último término:
$$E[f(X)]\ge f(\mu).$$
Esta demostración supone que las cantidades usadas están bien definidas e integrables. La versión general también cubre funciones convexas no diferenciables mediante rectas de soporte, bajo las condiciones correspondientes.

## 4. Ejemplos económicos

Con f(x)=x²:
$$E[X^2]\ge(E[X])^2,$$
que equivale a Var(X)≥0 cuando existe el segundo momento.

El logaritmo es cóncavo, porque su segunda derivada es −1/x²<0 para x>0. Jensen se invierte:
$$E[\ln W]\le\ln E[W].$$
Si W vale 50 o 150 con igual probabilidad, E[W]=100, pero:
$$E[\ln W]=\ln\sqrt{50\cdot150}=\ln(86.6025\ldots)<\ln100.$$
Esto cuantifica una consecuencia de la curvatura; no autoriza a identificar toda preferencia de riesgo con utilidad logarítmica.

## Ejercicios con solución

1. ¿−x² es convexa? No: es cóncava, con segunda derivada −2.
2. Minimiza (x−3)²+2: derivada 2(x−3), mínimo global x=3, valor 2.
3. Para X con valores 0 y 2 igualmente probables, f(E[X])=1 y E[f(X)]=2 si f=x².
4. ¿E[eˣ]=e^(E[X]) siempre? No. Convexidad da ≥, si las esperanzas existen; con variación no trivial e integrabilidad, la desigualdad es estricta.

**Límite:** antes de usar Jensen, comprueba dominio, curvatura e integrabilidad. No se puede aplicar ln a valores no positivos.
