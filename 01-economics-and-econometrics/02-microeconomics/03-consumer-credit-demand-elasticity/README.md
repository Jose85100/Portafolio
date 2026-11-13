# Consumer credit demand elasticity — identification and welfare

**Estado:** protocolo de investigación + notebook sintético. No se afirma identificación empírica de demanda real.

## 1. Objeto económico
El estimando es la elasticidad de demanda de **crédito solicitado** respecto al precio contractual, distinguiéndola de originación aprobada y desembolsada. En una demanda isoelástica:
```math
\log Q_i=\alpha+\varepsilon\log(1+r_i)+X_i'\gamma+u_i,
\qquad \varepsilon=\frac{\partial\log Q_i}{\partial\log(1+r_i)}.
```
No sustituir `log(1+r)` por `log r` sin explicitar que cambia el parámetro económico. El precio total puede incluir comisiones, seguros, plazos y condiciones; una tasa aislada puede no representar costo efectivo.

## 2. Selección y simultaneidad
El prestamista fija precios en función del riesgo, la competencia y la probabilidad de aprobación. Por ello `Cov(log(1+r_i),u_i)` puede ser distinto de cero. OLS estima una asociación, no necesariamente demanda. Además, observar solo créditos desembolsados condiciona en aprobación: si `A_i=1` depende de capacidad de pago y precio, `E[u_i|A_i=1]` puede ser distinto de cero.

Distinguir:
- margen extensivo: `P(Q_i>0|r_i,X_i)`;
- margen intensivo: `E[Q_i|Q_i>0,r_i,X_i]`;
- aprobación: `P(A_i=1|Q_i,r_i,X_i)`;
- incumplimiento posterior: riesgo de selección adversa, **no** demanda pura.

## 3. Identificación causal
Un instrumento `z_i` (variación de costo de fondeo o asignación aleatoria de oferta, si aplica) requiere:
```math
E[z_i u_i]=0,\quad Cov(z_i,\log(1+r_i))\ne 0.
```
La primera condición es sustantiva y no se prueba solo con regresiones. Un shock de fondeo puede afectar aprobación, plazos o liquidez directamente, violando exclusión. Si la asignación es experimental, documentar aleatorización, no cumplimiento, attrition, SUTVA y efectos heterogéneos. Con cumplimiento parcial, IV puede identificar un efecto local, no la elasticidad de toda la población.

En el caso simple, con variables centradas y sin controles, `beta_IV=Cov(z,y)/Cov(z,x)`. Con controles, aplicar Frisch–Waugh–Lovell antes de la razón. El código de [identificación](../../research-methods/) implementa este caso deliberadamente restringido y contrasta OLS/IV.

## 4. Especificación estadística
Para demanda con ceros, log-OLS pierde observaciones y cambia la población objetivo. Evaluar modelo de dos partes, Poisson pseudo-MLE con enlace log y exposiciones, o modelo estructural de elección discreta según el mecanismo. Para panel, considerar efectos fijos, shocks agregados y errores agrupados por unidad de asignación del precio. Evitar leakage al incluir información observada después de la decisión crediticia.

## 5. Simulación y evaluación
DGP recomendado: heterogeneidad de ingresos, riesgo latente, regla de pricing correlacionada con riesgo y variación instrumental. Escenarios: instrumento fuerte/débil, exclusión violada, selección por aprobación y heterogeneidad de elasticidad. Reportar sesgo, RMSE, cobertura, fuerza de primera etapa y distribución de estimaciones IV. La convergencia con tamaño muestral no elimina sesgo de exclusión.

## 6. Economía del negocio
La maximización ingenua de ingresos `R(r)=r Q(r)` ignora fondeo, LGD, EAD, costos operativos, capital y restricciones de protección al consumidor. Un problema de pricing responsable requiere optimizar beneficio **ajustado por riesgo** bajo límites de asequibilidad, equidad y cumplimiento regulatorio. La elasticidad de desembolsos puede aumentar artificialmente si cambia la tasa de aprobación.

## 7. Preguntas críticas
- ¿Medimos solicitudes, aprobaciones o saldos?
- ¿La elasticidad es respecto a tasa nominal, efectiva o costo total?
- ¿El instrumento afecta otras condiciones de oferta?
- ¿Qué ocurre si la aprobación es un collider?
- ¿Cómo cambia la elasticidad por ingresos, informalidad y riesgo?

## 8. Lecturas de base
- Angrist & Pischke (2009), *Mostly Harmless Econometrics*.
- Wooldridge (2010), *Econometric Analysis of Cross Section and Panel Data*.
- Imbens & Angrist (1994), *Identification and Estimation of Local Average Treatment Effects*, Econometrica.
- Karlan & Zinman (2008), *Credit Elasticities in Less-Developed Economies: Implications for Microfinance*, AER.

[Notebook actual](notebooks/01-estimation-and-robustness.ipynb) — datos sintéticos. [Biblioteca de identificación](../../research-methods/).
