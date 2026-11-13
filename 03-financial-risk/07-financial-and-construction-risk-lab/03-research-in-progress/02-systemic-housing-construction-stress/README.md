# Stress sistémico inmobiliario y construcción

**Área:** 03 research in progress  
**Estado:** diseño cuantitativo / investigación en construcción.

## Problema y objetivo
Propagación de shocks de tasas, empleo, costos y precios de vivienda hacia proyectos y contrapartes. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
Loss = g(rates, unemployment, materials, prices, delays)
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

## Validación y límites
Dependencias no lineales, escenarios severos plausibles y sensibilidad. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.

## Contexto público observado (no es validación)

Los [precios DANE IPVN](../../02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes/README.md), el [stock CEED](../../02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-unsold-completed-stock/README.md), los [flujos CEED](../../02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-housing-supply-flow/README.md), los [costos ICOCED](../../02-construction-enterprise-risk/06-materials-inflation-and-supply-chain/README.md) y la [sensibilidad DTF](../../02-construction-enterprise-risk/05-project-finance-covenants/observed-dtf-covenant-sensitivity/README.md) ofrecen factores observados para escenarios macro-sectoriales. No están unidos a pérdidas, defaults ni exposición sistémica de proyectos.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
