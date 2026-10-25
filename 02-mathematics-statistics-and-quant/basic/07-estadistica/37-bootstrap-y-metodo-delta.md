# 37. Bootstrap y método delta: incertidumbre de estadísticas transformadas

**Pregunta:** ¿cómo cuantificar incertidumbre cuando el estimador no es una simple media?  
**Objetivo:** derivar una aproximación analítica y entender qué reproduce el remuestreo. **Antes:** Taylor, inferencia y varianza.

## 1. Método delta desde Taylor

Supón que:
$$\sqrt n(\hat\theta-\theta)\xrightarrow{d}N(0,\tau^2).$$
Si g es diferenciable en θ:
$$g(\hat\theta)-g(\theta)
=g'(\theta)(\hat\theta-\theta)+o_p(n^{-1/2}).$$
Bajo las condiciones de esta aproximación:
$$\sqrt n[g(\hat\theta)-g(\theta)]\xrightarrow{d}
N(0,[g'(\theta)]^2\tau^2).$$
Esta es la versión de primer orden. Si g'(θ)=0, la escala y distribución informativas pueden depender del segundo orden; no debemos concluir que no existe incertidumbre.

## 2. Ejemplo con logaritmo de una media

Para datos IID positivos de media μ>0 y varianza σ² finita, g(μ)=ln μ y g'(μ)=1/μ. Aproximamos:
$$\operatorname{Var}(\ln\bar X)\approx\frac{\sigma^2}{n\mu^2}.$$
Sustituimos μ por x̄ y σ por s:
$$\widehat{SE}(\ln\bar X)=\frac{s}{\sqrt n\,\bar x}.$$
Si x̄=100,s=20,n=100, el error estándar es 0.02. Un intervalo normal aproximado en escala logarítmica:
$$\ln100\pm1.96(0.02).$$
Exponenciar extremos produce aproximadamente [96.16,104.00]. El intervalo no es simétrico en la escala original y conserva positividad.

Se está estimando ln(E[X]), no E[ln X]. Jensen explica por qué son cantidades diferentes.

## 3. Qué hace el bootstrap no paramétrico

Dados n datos observados, construimos una distribución empírica que asigna masa 1/n a cada observación. Para cada réplica:

1. Muestrea n observaciones con reemplazo desde esa distribución.
2. Calcula de nuevo la estadística T*.
3. Repite B veces y estudia su dispersión.

La desviación estándar de T* estima el error estándar bootstrap. Un intervalo percentil usa los cuantiles empíricos 2.5% y 97.5% de las réplicas. Es una receta concreta, no una garantía universal de cobertura exacta.

Fijar una semilla permite reproducir una corrida; aumentar B reduce error Monte Carlo del remuestreo, pero no agrega información original a la muestra.

## 4. Un caso que puede analizarse exactamente

Para la media bootstrap de una muestra x₁,…,xₙ, cada extracción tiene varianza empírica:
$$v_{\mathrm{emp}}=\frac1n\sum_i(x_i-\bar x)^2.$$
Las n extracciones bootstrap son independientes condicionalmente a los datos:
$$\operatorname{Var}_*(\bar X^*)=\frac{v_{\mathrm{emp}}}{n}.$$
Para datos (1,2,3), v_emp=2/3 y la varianza de la media bootstrap es 2/9. Podemos enumerar exactamente las 3³=27 muestras ordenadas y verificarlo, sin simulación.

Este ejemplo distingue la varianza empírica con denominador n de la estimación insesgada usual con denominador n−1.

## 5. Cuándo el remuestreo ingenuo falla

Si hay dependencia temporal, remuestrear filas sueltas rompe la estructura. Un bootstrap por bloques busca preservarla, pero requiere definir bloques y supuestos.

Si la muestra no contiene un evento raro, el bootstrap empírico no inventa esa cola ausente. Estadísticas en fronteras, máximos o problemas no regulares también pueden necesitar métodos especiales.

## Ejercicios y soluciones

1. Para g(θ)=θ², la derivada es 2θ; el delta de primer orden da varianza aproximada 4θ²Var(θ̂).
2. ¿Qué ocurre en θ=0? El primer orden se anula; hace falta estudiar segundo orden.
3. ¿Pasar de B=1000 a B=100000 corrige sesgo de selección? No.
4. En datos (1,2,3), el error estándar bootstrap exacto de la media es √2/3≈0.4714.

**Regla de estudio:** declara el parámetro objetivo, luego el estimador y después el método de incertidumbre; ese orden evita interpretar el intervalo de una cantidad como el de otra.
