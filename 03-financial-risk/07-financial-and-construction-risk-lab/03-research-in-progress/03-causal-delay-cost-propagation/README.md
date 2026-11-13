# Causalidad entre retrasos y sobrecostos

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Pregunta y alcance
Modelo estructural causal de dependencias y shocks. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
Cost_t = f(Delay_t, Prices_t, Scope_t, U_t)
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Identificación causal y sensibilidad a confusores. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Contexto público observado (no es validación)

Los [costos históricos ICOCED aplicados a escenarios de caja](../../02-construction-enterprise-risk/01-project-cashflow-at-risk/observed-icoced-cost-scenarios/README.md) y los [registros de suspensión/reanudación SECOP](../../02-construction-enterprise-risk/02-schedule-cost-overrun/observed-secop-work-suspensions/README.md) contextualizan shocks de costo y eventos administrativos. No hay enlace por obra, exposición a costo final, contrafactual ni identificación del efecto causal.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
