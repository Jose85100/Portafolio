# Optimización de coberturas

**Estado:** diseño con sensibilidad reproducible de mercado bajo coberturas ideales; no es optimización calibrada ni validada.

## Pregunta y alcance
Optimización de costo y riesgo de FX/tasas. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
min_h E[Loss(h)] + lambda*CVaR(Loss(h))
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Eficacia fuera de muestra, costos y basis risk. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Evidence gap

The neighboring TRM/DTF companion uses hypothetical balances; there are no observed exposures, executed hedges, hedge costs, or outcome records to optimize against. The new [observed-factor hedge scenario](observed-banrep-hedge-scenarios/README.md) demonstrates how observed market changes would scale under explicitly idealized hedge ratios. It is a sensitivity, not an optimization or validation. See [DATA_GAP.md](DATA_GAP.md) for the evidence needed to close the application gap.
