# 04. Escenarios macroeconómicos, no linealidad y riesgo prospectivo

## 1. Principio de información prospectiva

La medición debe incorporar información razonable y sustentable sobre condiciones actuales y previsiones económicas. La ponderación de escenarios es una técnica de aproximación de la expectativa; **no existe una exigencia universal de exactamente tres escenarios ni de pesos fijos 20/60/20**. Un escenario central por sí solo puede ser insuficiente si la relación entre variables macro y pérdidas es no lineal.

Sea \(M_{t:t+H}\) una trayectoria macroeconómica aleatoria. La medición conceptual es

\[
ECL_t=\int ECL_t(m)\,dF_t(m),
\]

aproximada mediante cuadratura o escenarios:

\[
\widehat{ECL}_t=\sum_{s=1}^S w_s ECL_t(m_s),\quad
w_s\ge0,\quad\sum_s w_s=1.
\]

El error depende de discretización de escenarios, pesos, incertidumbre paramétrica y especificación del modelo.

## 2. No linealidad y desigualdad de Jensen

Si \(g(m)=ECL(m)\) es convexa en una variable de estrés y \(M\) es aleatoria,

\[
\mathbb E[g(M)]\ge g(\mathbb E[M]).
\]

**Demostración:** por convexidad \(g(y)\ge g(x)+g'(x)(y-x)\); fijando \(x=\mathbb E[M]\) y tomando esperanza, el término lineal desaparece. Por ello, sustituir la distribución macro por su promedio puede subestimar ECL cuando la función de pérdidas es convexa. Si la función no es convexa, la dirección del sesgo no está garantizada.

Ejemplo puramente ilustrativo: pérdidas 2, 4 y 12 con probabilidades 0.2, 0.6 y 0.2 generan ECL \(=0.2(2)+0.6(4)+0.2(12)=5.2\). Usar solo el escenario central produce 4, una diferencia de 1.2 (30% respecto al central). No es una estimación de cartera real.

## 3. Modelo de PD condicional macro

Una especificación:

\[
\operatorname{logit}(h_{i,k,s})=
\alpha_k+\beta^\top X_{i,t}+
\gamma_1 U_{t+k,s}+
\gamma_2 \Delta PIB_{t+k,s}+
\gamma_3 r_{t+k,s}+
\gamma_4 U_{t+k,s}\Delta PIB_{t+k,s}.
\]

El término de interacción permite amplificación durante contracción. Los coeficientes no deben interpretarse causalmente sin diseño de identificación: desempleo, crecimiento y tasas están correlacionados y pueden responder endógenamente al ciclo crediticio. La extrapolación fuera de soporte histórico requiere límites y sensibilidad.

Para LGD, un modelo de recuperaciones condicionado en macro puede vincular precios de garantías, desempleo y tiempos de recuperación. Para EAD, modelar utilización contingente de líneas y restricciones de liquidez. Mantener **el mismo escenario** en los tres componentes evita combinaciones incoherentes, pero no sustituye el modelado de dependencia residual.

## 4. Escenarios y vintages

Cada corrida debe registrar: fecha de pronóstico, fecha de publicación, vintage, fuente, unidad, transformación, escenario, probabilidad, horizonte, supuestos y versión de modelo. No usar series macro revisadas posteriormente para simular lo que se habría conocido en el corte histórico. Para backtesting, reconstruir pronósticos disponibles en cada fecha; si no existen, marcar el experimento como contrafactual y no como validación histórica genuina.

## 5. Calibración de pesos y severidad

Los pesos son probabilidades o aproximaciones justificadas, no decisiones estéticas. Contrastar escenarios con distribuciones históricas y previsiones externas; verificar coherencia conjunta de PIB, desempleo, inflación, tasas y tipo de cambio. Evitar choques simultáneos físicamente o económicamente contradictorios salvo que se modelen explícitamente. Evaluar elasticidades

\[
\epsilon_{ECL,x}=
\frac{\partial ECL}{\partial x}\frac{x}{ECL},
\]

cuando \(x\neq0\), y diferencias finitas para variables con cero o unidades problemáticas. Una sensibilidad numérica no demuestra causalidad.

## 6. Riesgo de modelo

Separar: incertidumbre aleatoria de escenarios, incertidumbre de parámetros, cambio estructural y error de especificación. Estimar intervalos mediante bootstrap por cohorte y simulación posterior de parámetros; si se usa un enfoque bayesiano, reportar sensibilidad a priors y convergencia. Los overlays de juicio experto deben tener hipótesis, importe, fecha de caducidad, propietario, criterio de reversión y prohibición de doble contabilización.

## 7. Pruebas de estrés

La ECL IFRS 9 ponderada por probabilidad y el stress test extremo son objetos distintos. El stress test informa sensibilidad, solvencia y vulnerabilidad; no debe sustituirse mecánicamente la ECL contable por el resultado de un escenario adverso de probabilidad no justificada. Informar contribución de PD, LGD, EAD y horizonte mediante descomposiciones con orden de sustitución documentado o valores de Shapley cuando existan interacciones.
