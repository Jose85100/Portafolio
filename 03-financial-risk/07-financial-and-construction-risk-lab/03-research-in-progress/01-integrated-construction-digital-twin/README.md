# Gemelo cuantitativo de riesgo de constructora

**Área:** 03 research in progress  
**Estado:** diseño cuantitativo / investigación en construcción.

## Problema y objetivo
Integración de avance físico, cronograma, caja, preventas y shocks de mercado. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
X_{t+1}=f(X_t, actions_t, shocks_t)
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

## Validación y límites
Identificabilidad, calibración temporal y pruebas contrafactuales. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.

## Contexto público observado (no es validación)

El [flujo CEED](../../02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-housing-supply-flow/README.md) aporta actividad agregada; los [escenarios de costo ICOCED](../../02-construction-enterprise-risk/01-project-cashflow-at-risk/observed-icoced-cost-scenarios/README.md), [precios IPVN](../../02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes/README.md) y [suspensiones SECOP](../../02-construction-enterprise-risk/02-schedule-cost-overrun/observed-secop-work-suspensions/README.md) cubren factores parciales. No hay integración de datos físicos, cronogramas y caja por obra ni gemelo implementado.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
