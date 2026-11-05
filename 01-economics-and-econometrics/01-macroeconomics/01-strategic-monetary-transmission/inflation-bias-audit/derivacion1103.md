# Incremento 2026-11-03 — varianza bajo persistencia conocida

## Pregunta y estado de la contribución

¿Cómo alimentar el mismo módulo de pérdida de política monetaria cuando el shock es persistente y la varianza marginal no está observada? La pregunta amplía el programa de auditoría de varianza (29–02 nov) con una dependencia explícita. La corrida usa procesos sintéticos; no identifica shocks macroeconómicos ni valida un banco central real. Se clasifica como **adaptación de ingeniería + auditoría numérica** de momentos y GLS conocidos, no como resultado científico original.

## Modelo, unidades y dominio

Sea \(X_t=\mu+U_t\), \(U_t=\rho U_{t-1}+\eta_t\), \(|\rho|<1\), \(\eta_t\sim iid\;N(0,v(1-\rho^2))\). Bajo estacionariedad, \(\operatorname{Var}(U_t)=v\) (unidades de shock al cuadrado) y \(\gamma(h)=v\rho^{|h|}\). En la aplicación monetaria previa, \(v\) entra como varianza de shocks en la pérdida social; no es volatilidad estimada de datos macro reales.

## Fórmula anterior y limitación

El estimador anterior para shocks independientes usaba \(\hat v_{iid}=n^{-1}\sum_t(X_t-\bar X)^2\) y un intervalo \(\chi^2\) con \(n-1\) grados de libertad. Si hay AR(1), las observaciones no son independientes: la ley exacta de \((n-1)s^2/v\sim\chi^2_{n-1}\) deja de aplicar. Para el incremento pareado previo \(W_t=(X_t-X_{t-1})^2/2\), \(E[W_t]=v(1-\rho)\); ignorar dependencia confunde la varianza marginal con la varianza de una diferencia.

## Derivación del estimador de incrementos

Defínase \(D_t=X_t-X_{t-1}=U_t-U_{t-1}\). Entonces

\[
\operatorname{Var}(D_t)=2v(1-\rho),\qquad
\operatorname{Cov}(D_t,D_{t+h})=-v(1-\rho)^2\rho^{h-1},\quad h\ge1.
\]

La segunda igualdad sale de \(2\gamma(h)-\gamma(h-1)-\gamma(h+1)\). Por tanto el estimador corregido es

\[
Z_t=\frac{D_t^2}{2(1-\rho)},\qquad \hat v_P=\frac1m\sum_{t=1}^m Z_t,\quad m=n-1,
\]

y \(E[Z_t]=v\). Para variables gaussianas conjuntas, Isserlis da \(\operatorname{Cov}(D_t^2,D_s^2)=2\operatorname{Cov}(D_t,D_s)^2\). De aquí

\[
\frac{\operatorname{Var}(\hat v_P)}{v^2}=c_{m,\rho}
=\frac{2m+(1-\rho)^2\sum_{h=1}^{m-1}(m-h)\rho^{2(h-1)}}{m^2}.
\]

El intervalo usa Chebyshev en error relativo, no en error absoluto. Para \(\epsilon=\sqrt{c_{m,\rho}/\alpha}<1\), \(P(|\hat v_P/v-1|\ge\epsilon)\le\alpha\), de modo que

\[
v\in\left[\frac{\hat v_P}{1+\epsilon},\frac{\hat v_P}{1-\epsilon}\right]
\quad\text{con cobertura al menos }1-\alpha.
\]

Si \(\epsilon\ge1\), el límite superior no es finito: el código **se abstiene**. La garantía requiere normalidad conjunta y \(\rho\) conocido; no se conserva para \(\rho\) estimado, errores pesados, no estacionariedad ni varianza cambiante.

## Baseline competitivo: GLS exacto con \(\rho\) conocido

Se blanquea la serie mediante

\[
Z_0=X_0,\quad Z_t=\frac{X_t-\rho X_{t-1}}{\sqrt{1-\rho^2}},\qquad
H_0=1,\quad H_t=\frac{1-\rho}{\sqrt{1-\rho^2}}.
\]

Bajo el modelo, \(Z=H\mu+\sqrt v\,e\), \(e\sim N(0,I)\). Estimar \(\mu\) por GLS/OLS en el dominio blanqueado deja \(RSS/v\sim\chi^2_{n-1}\); se invierte esa distribución para el intervalo exacto. La construcción \(O(n)\) es algebraicamente equivalente a GLS denso; el test la contrasta numéricamente contra \((X-\hat\mu)'R^{-1}(X-\hat\mu)/(n-1)\).

## Propiedades, casos límite y relación entre métodos

- Conserva insesgamiento del estimador de incrementos al dividir por \(1-\rho\), para \(|\rho|<1\); no convierte incrementos solapados en observaciones independientes.
- En \(\rho=0\), los incrementos aún se solapan: \(\operatorname{Cov}(D_t,D_{t+1})=-v\). Omitir esa covarianza subestima la varianza del estimador.
- Al acercarse \(\rho\) a uno, \(1-\rho\) se aproxima a cero; la corrección amplifica ruido y el intervalo Chebyshev puede abstenerse en muestras chicas.
- El GLS exacto requiere conocer \(\rho\) sin error. Estimarlo cambia la distribución y exige nueva teoría o bootstrap apropiado.
- El intervalo iid se conserva sólo como ablación mal especificada, no como baseline competitivo bajo dependencia.

No se cambia la función de pérdida monetaria ni la ecuación de discreción. Cambia el módulo que provee el parámetro \(v\). En el límite de shock independiente, la varianza del nivel puede estimarse directamente; el método de diferencias no es equivalente en eficiencia, aunque la corrección \(1-\rho\) mantiene insesgamiento.

## Tres ideas evaluadas

1. **Intervalo por diferencias de primer orden y covarianzas gaussianas:** seleccionado; extensión acumulativa natural, derivable, ejecutable, con abstención explícita.
2. **GLS/Prais–Winsten exacto:** retenido como comparación/oráculo competitivo y no como novedad; eficiente bajo \(\rho\) conocido y supuestos gaussianos.
3. **Bootstrap/HAC o estimar \(\rho\):** diferido; requiere estudiar error de primer paso, longitud de bloque o identificación de \(\rho\), y añadir una comparación justa. Una implementación exploratoria no debe confundirse con un intervalo con cobertura probada.

## Evidencia y condición de validez

La simulación fija \(v=1\), \(\mu=0\), \(n\in\{64,256\}\), \(\rho\in\{0,0.5,0.9,0.95\}\), 90 réplicas por celda y confianza nominal 90%. El umbral predefinido H1 es que el límite inferior Wilson 95% de la cobertura empírica GLS sea al menos 0.80 en cada celda. Es una regla de cribado Monte Carlo, no una prueba del teorema de cobertura. Se informa cada falla; no se retocan semillas ni umbral tras ver resultados. Resultados en `results/dependent-*.csv/json` y figura ejecutada `results/dependent-interval.png`.
