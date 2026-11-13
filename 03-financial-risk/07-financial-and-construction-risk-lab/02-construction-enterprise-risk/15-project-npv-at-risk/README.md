# NPV-at-Risk y rentabilidad

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Aplicación observada de factores públicos

El [companion DANE de sensibilidad NPV](observed-dane-npv-sensitivity/README.md) aplica cambios trimestrales IPVN nacionales y el índice de concreto ICOCED Bogotá/Cundinamarca a flujos de caja hipotéticos. Produce sensibilidad histórica reproducible, no NPV de una obra, pronóstico, VaR ni validación de riesgo. Los flujos y la tasa de descuento son supuestos declarados.

## Evidencia pública y brecha

Las series DANE de costos de construcción, precios de vivienda y avalúos residenciales, y las tasas públicas BanRep disponibles en otras rutas permiten parametrizar escenarios macroeconómicos ilustrativos. No aportan presupuestos versionados, cronogramas de desembolso, ventas/preventas, deuda, impuestos ni flujos realizados de una obra identificable. Por eso este repositorio no afirma validación de NPV-at-Risk. La [brecha de datos](DATA_GAP.md) separa esos factores de contexto de los flujos de caja y resultados requeridos por proyecto.

## Pregunta y alcance
Distribución del VAN, TIR y pérdida de margen. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
NPV = sum_t CF_t/(1+r)^t
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Sensibilidad de descuento, escenarios y sesgo de estimación. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.
