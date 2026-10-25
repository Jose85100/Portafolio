# 4. Cálculo diferencial: del cambio promedio al marginal

**Objetivo:** entender límite, derivada, regla de la cadena y condiciones de optimización.

## Límite y continuidad

Un límite describe a qué valor se aproxima una expresión cuando la entrada se acerca a un punto. En $(x^2-1)/(x-1)$, el valor en 1 no existe, pero para $x\ne1$ la expresión es $x+1$; su límite cuando $x\to1$ es 2.

Continuidad en $a$ exige que $f(a)$ exista y coincida con el límite. Tener límite no basta. Una aproximación numérica sugiere un límite; por sí sola no lo demuestra.

## Derivar desde la definición

La pendiente promedio es $[f(x+h)-f(x)]/h$. Para $f(x)=x^2$:
$$\frac{(x+h)^2-x^2}{h}=2x+h,\quad h\ne0.$$
Al tomar $h\to0$, obtenemos $f'(x)=2x$. La derivada es pendiente local y tasa instantánea. Si $x$ mide tiempo y $f$ dinero, sus unidades son dinero por unidad de tiempo.

Reglas: $(x^n)'=nx^{n-1}$ donde corresponda; $(e^x)'=e^x$; $(\ln x)'=1/x$ para $x>0$. La derivada de una suma es la suma de derivadas. La regla de la cadena da $(f(g(x)))'=f'(g(x))g'(x)$: para $(3x+1)^2$ resulta $6(3x+1)$.

## Optimización con restricciones de dominio

Sea beneficio $\pi(q)=10q-q^2-9$ para $q\ge0$. La derivada $10-2q$ se anula en 5. La segunda derivada es $-2<0$: hay máximo local. Además
$$\pi(q)=16-(q-5)^2,$$
lo que prueba máximo global en $q=5$, con beneficio 16.

No todo punto estacionario es extremo: $x^3$ tiene derivada cero en 0 y sigue creciendo. En un intervalo cerrado hay que comparar también los extremos del intervalo.

Para varias variables, el gradiente reúne derivadas parciales. En $f(x,y)=x^2+3y^2$, $\nabla f=(2x,6y)$. Una parcial cambia una variable manteniendo la otra fija; no representa automáticamente el efecto total de una intervención económica.

## Ejercicios y soluciones

1. Deriva $3x^2-4x+7$: $6x-4$.
2. Minimiza $(x-2)^2$ en $[3,5]$: el estacionario 2 está fuera; mínimo en 3, valor 1.
3. Deriva $\ln(1+x^2)$: $2x/(1+x^2)$.
4. Para $Q=AP^{-2}$ con $A,P>0$, la elasticidad es $(dQ/dP)(P/Q)=-2$. Es adimensional, a diferencia de la pendiente.

**Límite computacional:** una diferencia con $h$ diminuto puede perder precisión por cancelación; menor paso no siempre significa menor error.
