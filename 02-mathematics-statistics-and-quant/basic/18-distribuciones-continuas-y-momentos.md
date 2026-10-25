# 18. Distribuciones continuas: densidad, acumulada y momentos

**Objetivo:** construir una distribución completa y derivar sus principales características.  
**Prerrequisitos:** probabilidad e integración. **Pregunta guía:** ¿por qué una densidad no es la probabilidad de un punto?

## 1. De una densidad a una probabilidad

Una densidad f cumple f≥0 e ∫f=1. La probabilidad de un intervalo es:
$$P(a\le X\le b)=\int_a^bf(x)dx.$$
Para una variable con densidad, P(X=x)=0: un punto tiene longitud cero, aunque puedan observarse valores puntuales. La densidad tiene unidades inversas a X; no es una probabilidad adimensional por sí sola.

Definimos F(x)=P(X≤x). Donde corresponde, F'=f. F es no decreciente, tiende a cero hacia −∞ y a uno hacia +∞.

## 2. Construir un ejemplo desde cero

Supón f(x)=cx para 0≤x≤2, y cero fuera. Para normalizar:
$$1=\int_0^2cx\,dx=c[x^2/2]_0^2=2c,$$
así que c=1/2. La acumulada completa es:
$$
F(x)=\begin{cases}
0,&x<0,\\
x^2/4,&0\le x\le2,\\
1,&x>2.
\end{cases}
$$
Por ello P(1<X≤2)=F(2)−F(1)=1−1/4=3/4. Los extremos abiertos o cerrados no cambian el resultado porque no hay masas puntuales.

## 3. Derivar media y varianza

La esperanza pondera valores por densidad:
$$E[X]=\int_0^2x(x/2)dx=\frac12[x^3/3]_0^2=\frac43.$$
El segundo momento:
$$E[X^2]=\frac12\int_0^2x^3dx=2.$$
Para ver por qué Var(X)=E[X²]−μ², expande:
$$E[(X-\mu)^2]=E[X^2]-2\mu E[X]+\mu^2=E[X^2]-\mu^2.$$
Aquí:
$$\operatorname{Var}(X)=2-\frac{16}{9}=\frac29.$$
La desviación estándar es √2/3. No confundas E[X²] con E[X]²: su diferencia mide precisamente dispersión.

## 4. Cuantiles y simulación inversa

El cuantil qₚ satisface F(qₚ)=p para 0<p<1:
$$q_p^2/4=p\Rightarrow q_p=2\sqrt p.$$
La mediana es √2, diferente de la media 4/3. La distribución no es simétrica.

Si U es uniforme en (0,1), X=2√U tiene esta distribución:
$$P(2\sqrt U\le x)=P(U\le x^2/4)=x^2/4,\quad0\le x\le2.$$
Esto demuestra una forma de simularla; no se trata de escoger una transformación por conveniencia sin justificar su acumulada.

## 5. Exponencial y memoria

Para λ>0, f(t)=λe^(−λt), t≥0. Integrando:
$$F(t)=1-e^{-\lambda t},\qquad P(T>t)=e^{-\lambda t}.$$
La probabilidad condicional de esperar más de s+t, habiendo esperado s, es:
$$P(T>s+t\mid T>s)=\frac{e^{-\lambda(s+t)}}{e^{-\lambda s}}=e^{-\lambda t}.$$
Esta propiedad de falta de memoria es fuerte: no se aplica automáticamente a tiempos de mora, fallos o eventos reales.

## Ejercicios con solución

1. P(X≤1) en el ejemplo triangular creciente: 1/4.
2. Cuantil del 90%: 2√0.9≈1.89737.
3. Para exponencial con λ=0.5 por año, P(T>2)=e^(−1)≈0.36788. λ debe ser compatible con la unidad de t.
4. ¿Puede una densidad valer 2? Sí. La uniforme en [0,0.5] vale 2 y su integral total es 1.

**Límite:** las fórmulas integrales de momentos solo producen valores finitos cuando las integrales correspondientes convergen.
