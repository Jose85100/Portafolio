# 34. Binomial, Poisson y geométrica: elegir el experimento

**Pregunta:** ¿contamos éxitos en un número fijo de ensayos, eventos por intervalo o tiempo hasta un éxito?  
**Objetivo:** derivar tres distribuciones discretas y separar sus supuestos. **Antes:** combinatoria y esperanza.

## 1. Binomial: número fijo de intentos

Sean Xᵢ IID Bernoulli(p), i=1,…,n. Para K=ΣXᵢ:
$$P(K=k)=\binom nk p^k(1-p)^{n-k},\quad k=0,\ldots,n.$$
Hay n sobre k maneras de ubicar éxitos; cada patrón tiene esa probabilidad por independencia. El binomio de Newton garantiza que las probabilidades sumen (p+1−p)ⁿ=1.

Por linealidad de la esperanza y ausencia de covarianzas:
$$E[K]=np,\qquad\operatorname{Var}(K)=np(1-p).$$
Para n=10,p=0.2, P(K=2)=45·0.2²·0.8⁸≈0.301990. La esperanza es 2, pero ese valor aparece en solo alrededor del 30.2% de las repeticiones.

## 2. Poisson como límite de eventos raros

Toma p=λ/n y conserva λ>0 mientras n crece:
$$P(K=k)=\frac{n(n-1)\cdots(n-k+1)}{k!}
\left(\frac\lambda n\right)^k
\left(1-\frac\lambda n\right)^{n-k}.$$
Para k fijo, el producto de factores n se compensa con nᵏ y tiende a 1; el último término tiende a e^(−λ). Obtenemos:
$$P(K=k)=e^{-\lambda}\frac{\lambda^k}{k!},\quad k\ge0.$$
La serie exponencial normaliza la distribución.

Derivando momentos mediante cambio de índice:
$$E[K]=e^{-\lambda}\sum_{k\ge1}\frac{k\lambda^k}{k!}
=\lambda e^{-\lambda}\sum_{j\ge0}\frac{\lambda^j}{j!}=\lambda.$$
Igualmente E[K(K−1)]=λ², de donde Var(K)=λ.

Para λ=2, P(K=0)=e⁻²≈0.135335. λ es número esperado por el intervalo definido; si el intervalo cambia y la intensidad es constante, λ cambia proporcionalmente.

La igualdad media–varianza es una restricción, no una ley de los conteos reales. Heterogeneidad y agrupación pueden producir sobredispersión.

## 3. Geométrica: intentos hasta el primer éxito

Sea T el número del ensayo donde ocurre el primer éxito, con soporte {1,2,…}. Para T=t hacen falta t−1 fallos seguidos de un éxito:
$$P(T=t)=(1-p)^{t-1}p,\quad0<p\le1.$$
Como P(T>t)=(1−p)ᵗ:
$$E[T]=\sum_{t=0}^{\infty}P(T>t)=\frac1p.$$
La identidad de suma de colas se obtiene contando cada entero t como suma de t unos y reorganizando términos no negativos.

Con q=1−p, la serie geométrica y sus derivadas permiten obtener E[T(T−1)]=2q/p². Así:
$$\operatorname{Var}(T)=\frac{1-p}{p^2}.$$
Con p=0.2, media 5 y varianza 20. La esperanza cinco no pone un límite a la espera.

## 4. Convención y falta de memoria

Algunas fuentes definen el número de fallos antes del éxito, Y=T−1, con soporte desde cero. Entonces E[Y]=(1−p)/p. Ambas convenciones son válidas; mezclarlas causa errores de una unidad.

Para enteros s,t≥0:
$$P(T>s+t\mid T>s)=\frac{(1-p)^{s+t}}{(1-p)^s}=(1-p)^t.$$
La probabilidad de éxito por intento permanece constante; si hay aprendizaje, deterioro o dependencia, este modelo puede fallar.

## Ejercicios y soluciones

1. Binomial n=5,p=0.1: P(K=0)=0.9⁵=0.59049.
2. Poisson λ=3: P(K=1)=3e⁻³≈0.149361.
3. Geométrica p=0.25: E[T]=4 y P(T>3)=0.75³.
4. ¿Poisson impone un máximo de eventos? No: su soporte es infinito; binomial tiene máximo n.

**Criterio de elección:** define primero unidad, horizonte, independencia y qué se cuenta. Ajustar una distribución por semejanza visual no sustituye esa definición.
