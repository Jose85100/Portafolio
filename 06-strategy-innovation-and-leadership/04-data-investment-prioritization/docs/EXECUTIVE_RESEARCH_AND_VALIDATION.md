# Executive research & validation — 04-data-investment-prioritization

**Estado:** protocolo de fortalecimiento; no implica que las pruebas descritas ya hayan sido ejecutadas.

## Pregunta de decisión
Priorizar datos e iniciativas de IA. Comparar política actual (baseline), alternativa conservadora y política optimizada, con trazabilidad de supuestos y posibilidad de no actuar.

## Formulación y supuestos
max sum_i x_i V_i; sum_i x_i c_i <= B. Definir horizonte temporal, unidad monetaria, calendario de flujos, restricciones, información disponible al decidir y función de pérdida. No usar variables conocidas únicamente después de la decisión.

## Programa estadístico
Value of information, leakage, costo de integración y error de ROI. Separar entrenamiento, calibración y evaluación temporal; usar validación rolling-origin cuando haya series. Estimar intervalos de confianza mediante bootstrap por cohortes/bloques cuando corresponda. Reportar error de predicción, estabilidad paramétrica, sensibilidad a missingness y cambios de régimen. Con datos sintéticos, verificar únicamente invariantes y recuperación de parámetros conocidos; no inferir rendimiento real.

## Experimentos reproducibles
1. Baseline determinista y prueba de invariantes contables.
2. Perturbación univariada de parámetros ±10% y ±25%, indicando cuando no tiene sentido económico.
3. Escenarios conjuntos: fondeo caro, demanda débil, pérdidas altas y disrupción operativa.
4. Simulación Monte Carlo con semilla fija y estudio de error estándar O(N^-1/2), si hay muestreo independiente y varianza finita.
5. Ablación de supuestos, prueba de datos fuera de distribución y análisis de decisiones dominadas.
6. Pruebas de regresión y verificación de que restricciones duras nunca se violen silenciosamente.

## Entregables de comité
Ficha de decisión de una página: alternativas, beneficio esperado, pérdidas extremas, capital/caja consumidos, umbrales de no aprobación, sensibilidad, responsable, fecha de revisión y riesgos residuales. Adjuntar anexos de metodología, datos y resultados reproducibles.

## Caso fintech
Inversión en bureau, open finance y señales alternativas. Distinguir entidad vigilada/no vigilada y jurisdicción; la aplicabilidad regulatoria se valida por tipo de licencia y producto.

## Criterios de aceptación para nivel ejecutivo
- Dataset versionado y diccionario; sin información privada ni credenciales.
- Métrica de decisión, baseline y costos de error explícitos.
- Pruebas automáticas, evidencia de ejecución y reporte de limitaciones.
- Política de escalamiento y propietario de decisión.
- Ninguna afirmación de desempeño real sin datos externos o institucionales adecuados.
