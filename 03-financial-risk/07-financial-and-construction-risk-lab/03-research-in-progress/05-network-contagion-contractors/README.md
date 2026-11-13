# Contagio de contratistas

**Estado:** investigación diseñada; implementación pendiente. **No calibrado ni validado.**

## Pregunta y alcance
Red bipartita obras-proveedores y propagación de fallos. ¿En qué condiciones se materializa el riesgo y qué acciones de mitigación generan valor ajustado por riesgo?

## Modelo propuesto
```text
p_{t+1} = sigmoid(A*p_t + X*beta)
```
Especificar unidades, granularidad, horizonte, estados observables/latentes, supuestos de identificación y dependencias. Cuantificar incertidumbre de estimación, simulación y especificación.

## Datos y estimación
Requeridos según proyecto: ERP y cuentas contables, presupuestos originales y revisados, cronogramas, actas de avance, órdenes de compra, proveedores, ventas y desistimientos, contratos, deuda y covenants, datos geográficos, indicadores públicos DANE/BanRep/Camacol cuando proceda. Registrar disponibilidad histórica, calidad, fechas de observación y permisos de uso. Para series escasas usar regularización o pooling jerárquico y reportar incertidumbre.

## Validación y experimentación
Pruebas contra modelo independiente y shocks comunes. Separación temporal de entrenamiento/prueba, benchmarks simples, backtesting, calibración de probabilidades, sensibilidad, stress y reverse stress. No presentar precisión predictiva hasta medirla con datos reales.

## Plan de construcción
1. Contrato de datos y definición de target sin leakage.
2. Baseline reproducible y tests unitarios.
3. Modelo estadístico principal y cuantificación de incertidumbre.
4. Backtesting temporal y comparación con benchmark.
5. API/reportes, trazabilidad, límites y aprobación de riesgo de modelo.

## Productos esperados
Metodología, código, pruebas, escenarios, reporte de validación y dashboard de decisiones.

## Contexto público observado (no es validación)

El [proxy de extensiones SECOP](../../02-construction-enterprise-risk/04-contractor-counterparty-risk/observed-secop-works-extension-proxy/README.md), el [perfil financiero de contratistas](../../02-construction-enterprise-risk/04-contractor-counterparty-risk/observed-supersociedades-corporate-financial-proxy/README.md), la [base de insolvencia](../../01-corporate-financial-risk/06-counterparty-credit-exposure/observed-supersociedades-insolvency-context/README.md) y el [enlace administrativo de garantías a obras](../../02-construction-enterprise-risk/14-surety-performance-bond-risk/README.md) aportan contexto separado sobre entidades y contratos. No conforman una red longitudinal de dependencias ni identifican propagación de pérdidas.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
