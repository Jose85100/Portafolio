# 02. Cambios de régimen, volatilidad y transiciones de crisis

## Pregunta
¿El riesgo de mercado aumenta gradualmente o mediante transiciones abruptas entre estados latentes de baja y alta volatilidad?

## Formulación
Sea \(S_t\in\{1,\ldots,K\}\) una cadena de Markov con matriz de transición \(P\), donde \(P_{ij}=\Pr(S_{t+1}=j\mid S_t=i)\) y \(\sum_jP_{ij}=1\). El retorno condicionado al estado:

\[
r_t\mid S_t=j,\mathcal F_{t-1}\sim
\mathcal N(\mu_j,\sigma_j^2)
\]

o Student-t para permitir colas pesadas. El filtro de Hamilton predice \(\pi_{t|t-1}=P^\top\pi_{t-1|t-1}\) y actualiza

\[
\pi_{t|t}(j)=
\frac{f_j(r_t)\pi_{t|t-1}(j)}
{\sum_\ell f_\ell(r_t)\pi_{t|t-1}(\ell)}.
\]

La verosimilitud observada es suma de logaritmos de los denominadores de normalización. No debe usarse estado suavizado \(\Pr(S_t\mid r_{1:T})\) como señal disponible en \(t\) para backtesting histórico: utiliza observaciones futuras.

## Interpretación
La duración media de un estado geométrico \(j\), cuando \(P_{jj}<1\), es \(1/(1-P_{jj})\). Esta duración depende de la hipótesis Markov homogénea; en crisis reales las probabilidades pueden variar con macro y liquidez.

## Estimación
EM/Baum–Welch, máxima verosimilitud con múltiples inicializaciones o inferencia bayesiana. Evitar label switching imponiendo orden identificable de volatilidades; comprobar convergencia y degeneración de varianzas. Comparar AIC/BIC con validación temporal, sin tratar los criterios como prueba definitiva de número de estados.

## Extensiones creativas
Modelar transición dependiente de spread bid–ask, utilización de colateral y retiros de financiación:

\[
\Pr(S_{t+1}=j\mid S_t=i,X_t)
=\frac{\exp(a_{ij}+b_{ij}^\top X_t)}
{\sum_\ell\exp(a_{i\ell}+b_{i\ell}^\top X_t)}.
\]

Permite estudiar si el deterioro de liquidez antecede cambios de régimen. La precedencia temporal no demuestra causalidad: spreads y volatilidad pueden responder al mismo shock.

## Validación
Calibración de probabilidades filtradas, log-score predictivo, PIT condicionado, comparación con GARCH y análisis de falsos cambios de régimen. No inferir un “atractor” matemático solo por visualizar clusters.
