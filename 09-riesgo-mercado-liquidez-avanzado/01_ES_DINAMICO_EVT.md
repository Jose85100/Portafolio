# 01. Expected Shortfall dinámico, filtración histórica y EVT

## Pregunta
¿Cuánto se subestima la pérdida extrema cuando el modelo de riesgo ignora agrupamiento de volatilidad, asimetría, colas pesadas y cambios de régimen?

## Modelo
Sea el retorno \(r_t=\mu_t+\sigma_t z_t\), con innovaciones \(z_t\) de media cero y varianza unitaria. Bajo GARCH(1,1),

\[
\sigma_t^2=\omega+\alpha(r_{t-1}-\mu_{t-1})^2+\beta\sigma_{t-1}^2,
\quad\omega>0,\;\alpha,\beta\ge0.
\]

Si \(\alpha+\beta<1\) y los shocks son estandarizados, la varianza incondicional es \(\omega/(1-\alpha-\beta)\). Si \(\alpha+\beta\ge1\), esta expresión deja de definir varianza estacionaria finita; un ajuste numérico que converja no garantiza estacionariedad.

Para pérdida \(L=-r\), defina

\[
VaR_q(L)=\inf\{x:\Pr(L\le x)\ge q\},
\qquad ES_q(L)=\frac{1}{1-q}\int_q^1 VaR_u(L)\,du.
\]

La filtración histórica (FHS) obtiene residuos \(\hat z_t=(r_t-\hat\mu_t)/\hat\sigma_t\) y simula \(r_{T+1}^{(b)}=\hat\mu_{T+1}+\hat\sigma_{T+1}\hat z_{j_b}\). La reescalación permite conservar estructura empírica de colas, bajo la hipótesis de innovaciones aproximadamente intercambiables tras el filtrado.

## Extremos
Para pérdidas sobre umbral alto \(u\), el exceso \(Y=L-u\mid L>u\) puede aproximarse con una Generalized Pareto Distribution:

\[
\Pr(Y>y)\approx(1+\xi y/\beta)^{-1/\xi},\quad
1+\xi y/\beta>0,\;\beta>0.
\]

Con probabilidad de excedencia empírica \(p_u\), un cuantil extrapolado cumple

\[
VaR_q\approx u+\frac{\beta}{\xi}
\left[\left(\frac{p_u}{1-q}\right)^\xi-1\right],
\]

para \(\xi\neq0\), con límite logarítmico si \(\xi=0\). Para \(\xi\ge1\), la media de cola de GPD no es finita; un ES extrapolado finito sería conceptualmente inválido.

## Backtesting
Kupiec contrasta frecuencia de excepciones, Christoffersen añade independencia de indicadores; ninguno por sí solo valida ES. Para ES, usar pruebas específicas de cola o funciones de scoring conjuntas VaR–ES, con supuestos y calibración adecuados. Separar selección de umbral EVT de evaluación fuera de muestra y cuantificar incertidumbre extrema con bootstrap temporal por bloques.

## Diseño experimental
Comparar HS, FHS-GARCH, Student-t condicional y EVT sobre residuos. Métricas: cobertura, clustering de excepciones, score VaR–ES, estabilidad por régimen y tiempos de cómputo. Realizar rolling-origin con ventanas de entrenamiento y embargo donde aplique.

## Riesgos
No asumir normalidad tras filtrar; no seleccionar umbral por mejor resultado de prueba; no tratar cuantiles extremos con 20 excedencias como precisos; no confundir ES de pérdidas de mercado con un requerimiento de capital regulatorio directamente calculable sin reglas de liquidez de horizontes, factores y agregación.
