# Enterprise Risk Advisory | 56 proyectos, 8 prácticas

**Estructura objetivo:** 7 proyectos por cada una de las 8 temáticas = **56**. Se conservan sin cambios los 24 proyectos previos; se añaden 32 nuevos proyectos S1. Los proyectos anteriores mantienen su estado y sus limitaciones, no se declaran implementados.

**Bases transversales:** [00-foundations/](00-foundations/) — matemática, estadística, arquitectura C++/Python/SQL, validación y gobierno. **Arquitectura de referencia:** [00-architecture/](00-architecture/).

Cada temática incluye **fundamentals/** (bases propias) y **siete carpetas de proyectos independientes**. Los fundamentos no se contabilizan como proyectos.

| Práctica | Proyectos | Carpeta |
|---|---:|---|
| Gobierno, ERM y estrategia | 7 | [01-erm-governance](01-erm-governance/) |
| Capital, tesorería y ALM | 7 | [02-capital-alm](02-capital-alm/) |
| Riesgo operacional y resiliencia | 7 | [03-operational-resilience](03-operational-resilience/) |
| Ciberseguridad, tecnología e IA | 7 | [04-cyber-ai](04-cyber-ai/) |
| Fraude, AML y cumplimiento | 7 | [05-financial-crime](05-financial-crime/) |
| Seguros, clima y conducta | 7 | [06-insurance-climate-esg](06-insurance-climate-esg/) |
| Valoración y contraparte | 7 | [07-valuation-counterparty](07-valuation-counterparty/) |
| Aseguramiento y transformación | 7 | [08-assurance-risk-data](08-assurance-risk-data/) |

## Alcance y madurez

- **24 programas existentes:** se preservan sus README y especificaciones.
- **32 programas nuevos:** README individuales con hipótesis, formulación, estadística, arquitectura C++/Python/SQL, experimentos y validación; todos **S1**.
- **56 proyectos en total:** catálogo metodológico; no 56 implementaciones.

## Notebooks con datos públicos: al menos dos por práctica

Estos primeros 17 ejercicios utilizan observaciones públicas y, cuando se indica, supuestos o proxies. Son análisis acotados; no validan los 56 modelos ni acreditan cumplimiento institucional. Cada notebook identifica fuente, método y limitaciones en su proyecto.

| Práctica | Aplicaciones |
|---|---|
| Gobierno y ERM | [Apetito: concentración de oferentes SFC](01-erm-governance/risk-appetite/aplicacion-datos-observados.ipynb) · [Estrés de fondeo con DTF](01-erm-governance/reverse-stress-risk-appetite/aplicacion-datos-observados.ipynb) |
| Capital y liquidez | [IRL histórico para ILAAP](02-capital-alm/ilaap/aplicacion-datos-observados.ipynb) · [Sensibilidad IRRBB con DTF](02-capital-alm/irrbb/aplicacion-datos-observados.ipynb) |
| Resiliencia | [Contexto UNGRD para continuidad](03-operational-resilience/business-continuity/01_contexto_ungrd.ipynb) · [Accidentalidad sectorial](03-operational-resilience/loss-distribution/01_contexto_accidentalidad.ipynb) |
| Ciber y tecnología | [Catálogo CISA y plazos](04-cyber-ai/technology-change/01_cisa_kev_priorizacion.ipynb) · [Proveedores y productos CISA](04-cyber-ai/cyber-attack-graphs/01_cisa_vendor_productos.ipynb) |
| Crimen financiero | [Composición de lista OFAC](05-financial-crime/aml-typologies/aplicacion_observada.ipynb) · [Completitud de campos OFAC](05-financial-crime/regulatory-controls/aplicacion_observada.ipynb) |
| Clima | [Reportes UNGRD](06-insurance-climate-esg/climate-risk/aplicacion_observada.ipynb) · [Precipitación NASA POWER](06-insurance-climate-esg/climate-hazard-credit/aplicacion_observada.ipynb) |
| Valoración y contraparte | [Sensibilidad CVA con FRED](07-valuation-counterparty/wrong-way-risk-xva/aplicacion-observada.ipynb) · [Excepciones de VaR para TES](07-valuation-counterparty/model-validation/aplicacion-observada.ipynb) |
| Aseguramiento de datos | [Cobertura y trazabilidad SFC](08-assurance-risk-data/risk-data-bcbs239/aplicacion-observada.ipynb) · [Conciliación de unidades SFC](08-assurance-risk-data/risk-data-reconciliation/aplicacion-observada.ipynb) · [Linaje SFC](08-assurance-risk-data/risk-model-lineage-graph/aplicacion-linaje-sfc.ipynb) |

Las listas OFAC y CISA son instantáneas de referencia; los reportes UNGRD no equivalen necesariamente a eventos únicos. Los escenarios de CVA, IRRBB y fondeo incorporan posiciones o supuestos hipotéticos. El análisis SFC comprueba el extracto, no la conformidad de una entidad con BCBS 239.

## Aplicaciones incorporadas posteriormente

Los nuevos casos profundizan temas adicionales. Las aplicaciones con supuestos y benchmarks fuera de dominio mantienen sus restricciones explícitas; el catálogo conserva proyectos sin notebook propio.

- **Capital y ALM:** [Euler de capital](02-capital-alm/capital-allocation-euler/aplicacion-observada.ipynb), [liquidez contingente](02-capital-alm/contingent-liquidity-optimization/aplicacion-observada.ipynb), [ICAAP](02-capital-alm/icaap/aplicacion-observada.ipynb), [capital y depósitos](02-capital-alm/capital-liquidity-feedback/aplicacion-observada.ipynb) y [balance estocástico](02-capital-alm/stochastic-balance-sheet-alm/aplicacion-observada.ipynb).
- **Resiliencia y ciberseguridad:** [duración de contención VCDB](03-operational-resilience/recovery-time-stochastic/benchmark-vcdb-contencion.ipynb), [drift con datos UCI](04-cyber-ai/ai-model-drift-risk/benchmark-uci-observado.ipynb) y [robustez adversarial con datos UCI](04-cyber-ai/adversarial-model-robustness/benchmark-uci-observado.ipynb).
- **Crimen financiero y seguros:** [priorización geográfica FinCEN](05-financial-crime/aml-alert-prioritization/aplicacion-fincen-estados.ipynb), [reservas chain ladder](06-insurance-climate-esg/insurance-reserving/aplicacion-cas-chainladder.ipynb) e [incertidumbre de factores](06-insurance-climate-esg/actuarial-reserve-uncertainty/aplicacion-cas-incertidumbre.ipynb).
- **Contraparte y aseguramiento:** [cotizaciones de opciones](07-valuation-counterparty/pricing-uncertainty-bounds/aplicacion-spy-bid-ask.ipynb) y [monitoreo estadístico SFC](08-assurance-risk-data/continuous-assurance-statistics/aplicacion-sfc-control-estadistico.ipynb).

La descarga de cotizaciones depende de la disponibilidad de Cboe; VCDB y CAS requieren acceso a sus fuentes en línea. Las simulaciones y perturbaciones son variables construidas sobre datos observados, no validación de desempeño institucional.

## Orden de implementación

1. Establecer contratos comunes y criterios de aceptación.
2. Implementar un motor verificable por práctica con tests y simulaciones.
3. Integrar escenarios, dependencia entre riesgos y validación independiente.
4. Publicar evidencias, resultados y decisiones solo tras evaluación reproducible.

## Fundamentación ampliada — 3 bases por temática

Cada una de las ocho prácticas tiene **tres documentos independientes de fundamentación**: matemática/teoría, estadística/econometría y computación/métodos numéricos. Son **24 fundamentos disciplinares**, separados de los **56 proyectos** (7 por práctica). La base transversal `00-foundations/` es compartida y no cuenta como proyecto.
