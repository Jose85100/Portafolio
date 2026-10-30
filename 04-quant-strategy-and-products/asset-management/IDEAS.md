# Ideas de investigación: asset management

Estas líneas amplían los MVP existentes de Markowitz, Black–Litterman, paridad de riesgo y rebalanceo con costos. El foco es convertir asignaciones estáticas en decisiones de inversión adaptativas, con restricciones reales y evaluación fuera de muestra.

## Cinco ideas

1. **Asignación multi-periodo con pasivos y metas**
   - Optimizar trayectorias de consumo, reservas y activos frente a pasivos futuros; comparar programación dinámica, control estocástico y optimización por escenarios.
   - Núcleo: minimizar la probabilidad/costo de incumplir metas bajo restricciones de liquidez y solvencia.

2. **Portafolios robustos a error de estimación**
   - Medir cuánto cambia la cartera cuando se perturban rendimientos esperados, covarianzas y correlaciones; contrastar shrinkage, incertidumbre elipsoidal y optimización distribucional.
   - Aporte: reportar estabilidad de pesos y arrepentimiento frente al óptimo ex post, además del Sharpe.

3. **Asignación de activos privados e ilíquidos**
   - Incorporar private credit, infraestructura y capital privado con valoraciones infrecuentes, flujos comprometidos, llamadas de capital y ventanas de salida.
   - Núcleo: optimización con caja por fecha, curvas de capital comprometido y límites de concentración.

4. **Portafolio tributario y de costos de tenencia**
   - Comparar rebalanceos antes y después de impuestos, comisiones, spreads y costos de custodia bajo reglas parametrizables por jurisdicción.
   - Aporte: identificar cuándo conviene mantener posiciones por costo fiscal y cuándo el beneficio esperado justifica vender.

5. **Asignación por escenarios macroeconómicos**
   - Traducir escenarios de tasas, inflación, tipo de cambio y crecimiento a distribuciones condicionadas de retornos; evaluar carteras que preserven objetivos en varios regímenes.
   - Núcleo: optimización robusta por escenarios con penalización explícita a pérdidas de meta y concentración.

## Estándar de desarrollo

Cada estudio debe declarar universo y frecuencia, fuentes/licencia de datos, supuestos, restricciones, benchmark simple, validación temporal sin fuga de información, métricas de costos y límites de interpretación. Entregar notebook reproducible, módulo Python y datos sintéticos cuando no haya datos públicos adecuados.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Optimización estática por periodo y matching de duración.** Base: Integrar metas y pasivos con decisiones de aporte y gasto en una política multi-periodo. **Innovación a probar:** Medir incumplimiento de metas fuera de muestra frente a LDI estático y política 60/40; probar shocks de tasas e inflación. **Prueba decisiva:** undefined
- **2. Covarianza histórica y shrinkage como estimadores convencionales.** Base: Construir cartera robusta a conjuntos explícitos de error en medias, correlaciones y colas. **Innovación a probar:** Comparar estabilidad de pesos y arrepentimiento neto frente a shrinkage, igual ponderación y óptimo ex post. **Prueba decisiva:** undefined
- **3. Media-varianza con activos líquidos y costos simples.** Base: Incorporar llamadas de capital, flujos privados e iliquidez en una optimización factible por fecha. **Innovación a probar:** Verificar caja en cada periodo y comparar ventas forzadas/costo con una cartera sin compromisos bajo estrés. **Prueba decisiva:** undefined
- **4. Rebalanceo por retorno antes de impuestos.** Base: Incorporar impuestos, lotes de costo, diferimiento y costos de operación a una regla única de rebalanceo. **Innovación a probar:** Comparar retorno neto de impuestos y tracking error con rebalanceo convencional en datos y reglas tributarias documentados. **Prueba decisiva:** undefined
- **5. Escenarios macro con probabilidades fijas.** Base: Optimizar contra incertidumbre en probabilidades y dependencia entre escenarios. **Innovación a probar:** Probar reducción de déficit de metas en escenarios no usados para calibrar sin sacrificar demasiado desempeño central. **Prueba decisiva:** undefined
