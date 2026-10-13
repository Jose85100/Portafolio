# Cash-Flow-at-Risk de proyectos de construcción

**Área:** 02 construction enterprise risk  
**Estado:** diseño cuantitativo / investigación en construcción (con prototipo Python inicial).

## Problema y objetivo
Motor mensual de costos, preventas, recaudos, hitos, deuda y caja con escenarios correlacionados. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
Cash_t = Cash_{t-1}+collections_t+drawdowns_t-costs_t-debt_service_t
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

## Validación y límites
Monte Carlo, calibración de distribuciones, stress y reverse stress. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.
