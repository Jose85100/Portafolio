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
