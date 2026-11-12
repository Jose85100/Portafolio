# Crédito de contrapartes

**Estado:** diseño de investigación con companion público de contexto de insolvencia. **No calibrado ni validado.**

El companion [Supersociedades: procesos de insolvencia](observed-supersociedades-insolvency-context/README.md) agrega el corte oficial por proceso y macrosector y conserva controles de esquema y hash. Describe el entorno concursal; no mide exposiciones, incumplimientos de obligaciones de nuestra cartera o recuperaciones, ni estima PD/LGD/EAD. La brecha de outcomes institucionales sigue abierta ([contrato de datos y validación](DATA_GAP.md)).

## Pregunta y alcance
PD/LGD/EAD para cuentas por cobrar y anticipos. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
EL = PD*LGD*EAD
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Calibración temporal, concentración y recuperación. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Evidence gap

Aggregate company accounts do not link a focal exposure to counterparty default and recovery outcomes. See [DATA_GAP.md](DATA_GAP.md).
