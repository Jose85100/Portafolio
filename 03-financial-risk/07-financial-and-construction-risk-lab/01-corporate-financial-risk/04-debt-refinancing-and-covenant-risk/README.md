# Refinanciación y covenants

**Estado:** diseño con sensibilidad reproducible de tasa pública y términos hipotéticos. **No calibrado ni validado para emisor.**

El companion [DSCR con tasa comercial observada](observed-banrep-dscr-sensitivity/README.md) muestra sensibilidad histórica para una deuda bullet interest-only hipotética. No aporta términos, breach, cura o resultados de una empresa.

## Pregunta y alcance
Probabilidad de breach por estructura de deuda y tasas. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
P(min_t DSCR_t < threshold)
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Stress de spreads, rollover y vencimientos. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Evidence gap

The BanRep loan-rate companion is aggregate market context; issuer debt schedules, signed covenant terms, breach/cure and refinancing outcomes remain unavailable. See [DATA_GAP.md](DATA_GAP.md).
