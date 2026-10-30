# Ideas de producto: motores cuantitativos

Esta carpeta convierte métodos cuantitativos en componentes ejecutables, reutilizables y comparables. Los modelos regulatorios, la calibración de PD/LGD/EAD y la validación de riesgo permanecen en [03-financial-risk](../../03-financial-risk/README.md). Aquí el énfasis es arquitectura numérica, interfaces, optimización y uso en decisiones de producto.

## Cinco ideas

1. **Motor de escenarios financieros reproducibles**
   - Generar trayectorias correlacionadas de tasas, FX, precios y flujos con semillas auditables y escenarios históricos e hipotéticos.
   - Entregable: API común Python/C++ y pruebas de paridad; no sustituye modelos regulatorios de riesgo.

2. **Motor de atribución marginal de capital y límites**
   - Descomponer consumo de presupuesto por instrumento, mesa, producto y cliente; comparar asignación marginal con reglas proporcionales.
   - Núcleo: contribuciones Euler cuando se cumplan las condiciones matemáticas y aproximaciones documentadas en los demás casos.

3. **Motor de colateral y llamadas de margen**
   - Simular exposición, haircuts, umbrales, frecuencia de margin call, retrasos de liquidación y disputa de garantías.
   - Aporte: analizar costo de liquidez y estabilidad de colateral bajo saltos y gaps, con trazas por operación.

4. **Motor de decisión riesgo–retorno para productos**
   - Evaluar límites de precio, plazo, cupo y elegibilidad mediante frontera de rentabilidad ajustada por capital y restricciones comerciales.
   - Enfoque de producto: comparación de decisiones y escenarios; los estimadores de riesgo se consumen como entradas versionadas.

5. **Motor de optimización de caja y pagos**
   - Elegir secuencia y momento de pagos, reservas operativas y fondeo intradía sujeto a costos, prioridades y tiempos de liquidación.
   - Núcleo: programación lineal entera o heurísticas verificables; reportar costo, retraso y restricciones activas.

## Contratos de ingeniería

Definir unidades, moneda, calendarios, tolerancias numéricas, manejo de datos faltantes y errores; fijar contratos de entrada/salida y casos de referencia. Medir precisión, convergencia, latencia y reproducibilidad. No presentar motores de demostración como producción o como sustituto de validación independiente.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Simulación con generadores independientes por clase de activo.** Base: Escenarios sincronizados, versionados y reproducibles con invariantes y shocks acoplados. **Innovación a probar:** Verificar repetibilidad, momentos/correlaciones objetivo y paridad entre implementaciones de referencia. **Prueba decisiva:** undefined
- **2. Asignación proporcional de presupuesto de capital.** Base: Atribución marginal con reconciliación matemática y restricciones por unidad o producto. **Innovación a probar:** Comprobar suma de contribuciones, estabilidad ante perturbaciones y utilidad frente a regla pro-rata. **Prueba decisiva:** undefined
- **3. Haircuts estáticos y calendario de margen fijo.** Base: Simular haircut, disputa, demora y liquidación como estados conjuntos de colateral. **Innovación a probar:** Comparar costo y déficit de garantía contra política fija en saltos, gaps y retrasos extremos. **Prueba decisiva:** undefined
- **4. Pricing por reglas manuales con métricas aisladas.** Base: Optimización conjunta de precio, plazo, cupo y elegibilidad con fronteras comerciales explícitas. **Innovación a probar:** Comparar margen ajustado por capital y tasa de aceptación con la regla vigente; comprobar restricciones en todos los casos. **Prueba decisiva:** undefined
- **5. Heurísticas de caja por prioridad fija.** Base: Optimización de pagos/fondeo con restricciones temporales, costos y contingencias. **Innovación a probar:** Medir costo y retrasos frente a FIFO y regla actual, incluyendo factibilidad y sensibilidad ante pagos faltantes. **Prueba decisiva:** undefined
