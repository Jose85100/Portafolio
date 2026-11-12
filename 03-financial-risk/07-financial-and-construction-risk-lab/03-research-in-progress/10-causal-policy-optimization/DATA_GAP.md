# Brecha de datos: optimización causal de políticas

**Corte:** 2026-11-11. **Estado:** propuesta S1; no hay panel público/institucional de políticas de mitigación asignadas a proyectos y outcomes comparables.

Las series públicas enlazadas en las rutas vecinas observan factores de mercado o actividad, por ejemplo precios de vivienda, tasas, licenciamiento y eventos administrativos. No indican qué proyecto recibió una política concreta de preventa, cobertura o financiación, cuándo se aplicó, qué alternativas eran elegibles ni el flujo de caja contrafactual. No identifican valor causal de una política o la política óptima.

## Datos mínimos para identificar efectos

- ID de proyecto seudonimizado, cohorte, fechas de decisión y periodo de elegibilidad.
- Política/tratamiento definido, intensidad, asignación, fecha de adopción, cambios y grupo de comparación.
- Covariables medidas antes de la decisión; presupuesto, riesgo, ubicación, etapa, mercado y restricciones de elegibilidad.
- Outcomes con fechas y vintage: costo, ingresos, preventas/cancelaciones, caja, atraso, default, uso/costo de cobertura y pérdidas.
- Variables de exposición a otros proyectos y políticas para evaluar interferencia/spillovers.
- Permisos, lineage, reglas para datos faltantes y definición aprobada del estimando.

## Puertas de validación

Definir el estimando antes de modelar; defender intercambiabilidad o instrumento/diseño cuasi experimental; revisar positividad, balance y spillovers; usar cross-fitting y benchmark transparente cuando proceda; separar temporalmente y por proyecto; ejecutar sensibilidad a confusión no observada; replicar los resultados de forma independiente; y acordar criterio de aceptación antes de evaluar una política. Sin asignación y outcome enlazados, no se estiman ATE, valor de política ni decisión óptima.
