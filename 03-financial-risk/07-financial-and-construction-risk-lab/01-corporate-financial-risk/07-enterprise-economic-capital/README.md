# Capital económico corporativo

**Estado:** especificación de capital económico con companion público de solvencia/deterioro. **El modelo de capital sigue sin implementar, calibrar ni validar.**

## Pregunta y alcance
Capital económico con agregación de riesgos dependientes. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
EC = VaR_99.5%(L)-E[L]
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Copulas, sensibilidad a cola y asignación Euler. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Evidence gap

El companion [SFC de solvencia y deterioro](observed-sfc-capital-loss-context/README.md) aporta contexto regulatorio y contable agregado; no estima pérdidas de cola ni capital económico institucional. El panel institucional de pérdidas y dependencias sigue faltando. Véase [DATA_GAP.md](DATA_GAP.md).

## Public regulatory context

The [SFC aggregate solvency and impairment context](observed-sfc-capital-loss-context/README.md) provides an official, reproducible sector benchmark for regulatory capital and accounting deterioration. It does not estimate VaR, ES, or corporate economic capital; the institutional loss/factor/dependency gap remains open.
