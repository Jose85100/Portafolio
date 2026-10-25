# 5. Cálculo integral: acumulación y área con signo

**Objetivo:** conectar sumas, antiderivadas, unidades y aproximación numérica.

## De rectángulos a una integral

Si un flujo $f(t)$ cambia con el tiempo, una aproximación de su acumulado es $\sum_i f(t_i)\Delta t_i$. Al refinar la partición, cuando existe el límite, aparece $\int_a^b f(t)\,dt$.

La integral tiene unidades de flujo por tiempo multiplicadas por tiempo. Si $f(t)$ está en pesos por mes y $t$ en meses, el acumulado está en pesos. Es área **con signo**: cantidades bajo el eje restan.

## Teorema fundamental

Si $f$ es continua y $F'=f$, entonces
$$\int_a^b f(x)\,dx=F(b)-F(a).$$
Para $f(x)=2x$, una antiderivada es $x^2$; entre 0 y 3 el acumulado es $9$. Las antiderivadas difieren en una constante: $\int2x\,dx=x^2+C$.

La regla de potencias es $\int x^n dx=x^{n+1}/(n+1)+C$ para $n\ne-1$ en intervalos donde se define. El caso $1/x$ produce $\ln|x|+C$ en intervalos que no cruzan cero.

## Aplicación al costo marginal

Si $C'(q)=2+0.1q$ y $C(0)=100$:
$$C(q)=100+\int_0^q(2+0.1s)ds=100+2q+0.05q^2.$$
Así $C(10)=125$. Integrar el costo marginal recupera el costo variable; hace falta la condición inicial para recuperar el costo total.

## Trapecios y error

En cada subintervalo, aproximamos por el área de un trapecio: $\Delta x[f(x_i)+f(x_{i+1})]/2$. Para $x^2$ entre 0 y 1, un trapecio da 0.5; dos dan 0.375; la integral exacta es $1/3$. Al duplicar subintervalos, el error suele disminuir aproximadamente por factor 4 si la función tiene segunda derivada continua y usamos una malla uniforme. No es una garantía universal para funciones singulares o discontinuas.

## Ejercicios y soluciones

1. Integra $3x^2$ entre 0 y 2: $[x^3]_0^2=8$.
2. Integra $x$ entre $-1$ y 1: cero, por simetría impar. El área geométrica total es 1, porque usa $|x|$.
3. ¿El valor de una densidad puede superar 1? Sí; su integral total debe ser 1. Una densidad uniforme en $[0,0.5]$ vale 2.
4. ¿Se puede calcular $\int_{-1}^1 1/x\,dx$ cancelando logaritmos? No: la integral impropia usual no converge; la singularidad exige estudiar ambos lados por separado.
