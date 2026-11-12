# Políticas de mitigación causal

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Pregunta y alcance
Evaluación de políticas de preventas, coberturas y financiación. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
V(pi)=E[Y(pi(X))]
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Positividad, identificación, OPE y sensibilidad. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Brecha de evidencia observada

Las series públicas de tasas, precios, licenciamiento, costos y eventos administrativos no identifican qué proyecto recibió cada política de preventa, cobertura o financiación ni los outcomes comparables bajo alternativas. Por eso la propuesta sigue S1 y no calcula un efecto causal ni recomienda una política. El contrato mínimo de tratamiento, elegibilidad, covariables previas, outcomes fechados y evaluación está en [DATA_GAP.md](DATA_GAP.md).

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Benchmark empírico de metodología

Se añadió [benchmark NSW](benchmark_nsw/README.md), un ejemplo ejecutable con asignación experimental y resultados observados de un programa de empleo. Permite practicar selección y evaluación de políticas fuera de muestra. Es evidencia metodológica en otro dominio: **no identifica efectos de coberturas, preventas ni financiación de proyectos de construcción**. La aplicación original permanece S1 y requiere los datos del contrato descrito en DATA_GAP.md.
