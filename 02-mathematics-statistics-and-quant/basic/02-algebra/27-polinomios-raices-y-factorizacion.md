# 27. Polinomios: raíces, factorización y multiplicidad

**Pregunta:** ¿cómo conecta una raíz con un factor y con la forma de la gráfica?  
**Objetivo:** deducir herramientas de resolución y reconocer cuándo una transformación añade soluciones. **Antes:** lecciones 1, 2 y 14.

## 1. Estructura de un polinomio

Un polinomio real es una suma finita:
$$P(x)=a_nx^n+\cdots+a_1x+a_0,\quad a_n\ne0.$$
n es el grado. No son polinomios x⁻¹ ni √x: sus exponentes no son enteros no negativos. Un polinomio no nulo de grado n tiene como máximo n raíces reales distintas; no necesariamente tiene n raíces reales.

## 2. Teorema del resto y factor

Dividir P por x−r permite escribir:
$$P(x)=(x-r)Q(x)+c,$$
donde c es constante porque el resto tiene grado menor que uno. Sustituir x=r da c=P(r). De aquí:
$$P(r)=0\iff P(x)=(x-r)Q(x).$$
Esta equivalencia justifica que encontrar una raíz permita extraer un factor.

**Ejemplo:** P=x³−6x²+11x−6. P(1)=0. Dividir por x−1 da x²−5x+6, que factoriza como (x−2)(x−3). Así:
$$P(x)=(x-1)(x-2)(x-3).$$
Expandir de nuevo o sustituir las raíces verifica el cálculo.

## 3. Deducir la fórmula cuadrática

Para ax²+bx+c=0, con a≠0, divide por a y completa el cuadrado:
$$x^2+\frac ba x=-\frac ca,$$
$$\left(x+\frac b{2a}\right)^2=\frac{b^2-4ac}{4a^2}.$$
Por tanto, sobre los reales cuando Δ=b²−4ac≥0:
$$x=\frac{-b\pm\sqrt{\Delta}}{2a}.$$
Si Δ>0 hay dos raíces distintas; si Δ=0, una raíz doble; si Δ<0 no hay raíces reales. Al trabajar sobre complejos, también se resuelve el último caso.

La forma de vértice:
$$P(x)=a\left(x+\frac b{2a}\right)^2-\frac{\Delta}{4a}$$
explica geométricamente tanto el vértice como el número de cruces del eje.

## 4. Multiplicidad y cambio de signo

Si P(x)=(x−r)ᵐQ(x), Q(r)≠0, la raíz r tiene multiplicidad m. Cerca de r, Q mantiene su signo por continuidad. Si m es impar, el factor (x−r)ᵐ cambia de signo; si m es par, no.

Para (x−1)²(x+2), la gráfica toca el eje en 1 sin cambiar de signo y cruza en −2. Esto también ayuda a construir tablas de signos para desigualdades polinómicas.

## 5. Elevar al cuadrado puede añadir soluciones

Resuelve √(x+2)=x. El dominio de la raíz requiere x≥−2, pero la igualdad exige además x≥0. Al cuadrar:
$$x+2=x^2\Rightarrow(x-2)(x+1)=0.$$
Aparecen 2 y −1. Solo 2 satisface la ecuación original; −1 daría 1=−1. La transformación original⇒cuadrada era válida, pero la recíproca necesitaba restricciones de signo.

## Ejercicios y soluciones

1. Factoriza x²−5x+6: (x−2)(x−3).
2. Resuelve 2x²−4x+2=0: 2(x−1)²=0; raíz doble 1.
3. ¿Cuántas raíces reales tiene x²+1? Ninguna, porque x²≥0.
4. Resuelve √(2x+3)=x. Debe x≥0; cuadrar da x=3 o −1. Solo 3 verifica √9=3.

**Límite numérico:** la fórmula cuadrática directa puede sufrir cancelación cuando b y √Δ son muy cercanos. Una identidad algebraicamente correcta no siempre es la mejor implementación en punto flotante.
