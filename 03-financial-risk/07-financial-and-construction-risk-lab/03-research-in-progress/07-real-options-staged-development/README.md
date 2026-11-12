# Opciones reales por etapas

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Pregunta y alcance
Decisión de iniciar, aplazar, expandir o abandonar. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
V_t = max(Exercise_t, E_t[V_{t+1}]/(1+r))
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Monte Carlo de mínimos cuadrados y política fuera de muestra. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Contexto público observado (no es validación)

El [licenciamiento ELIC](../../02-construction-enterprise-risk/03-presales-demand-and-cancellations/observed-dane-elic-supply-signal/README.md), los [precios IPVN](../../02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes/README.md), los [costos ICOCED](../../02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/README.md) y la [sensibilidad DTF](../../02-construction-enterprise-risk/05-project-finance-covenants/observed-dtf-covenant-sensitivity/README.md) contextualizan factores de mercado. No observan decisiones escalonadas, flujos por alternativa ni valores realizados de opciones reales.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
