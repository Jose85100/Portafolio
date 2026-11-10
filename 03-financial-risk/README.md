# Financial Risk Research

Crédito, mercado, liquidez, riesgo sistémico, IFRS 9 y stress testing integrado. Investigación y productos sujetos a validación empírica.

## Estructura

1. [Crédito](01-credit-risk/): [productos de crédito](01-credit-risk/credit-risk-products/) y [estrategia de cartera](01-credit-risk/credit-portfolio-strategy/): scoring, IFRS 9, cosechas, concentración, cópula, capital y apetito de riesgo. Incluye [fraude, anomalías y minimización de pérdida](01-credit-risk/fraud-and-anomaly-research/), con cuatro especialistas S1 y un motor S2 acotado a datos sintéticos.
2. [Mercado y modelos](02-market-and-model-risk/): VaR/ES, backtesting, GARCH, pruebas de estrés y validación (PSI/Gini).
3. [Liquidez de mercado](03-market-liquidity-research/): ES dinámico y EVT, regímenes de volatilidad, liquidez estocástica, espirales de liquidez y optimización de liquidez.
4. [Investigación avanzada](04-advanced-research/): siete propuestas metodológicas de crédito, IFRS 9, SIAR y control de cartera.
5. [Enterprise Risk Advisory](05-enterprise-risk-advisory/): 56 diseños metodológicos agrupados en ocho prácticas, con fundamentos separados.
6. [Motor de investigación cuantitativa](06-quantitative-research-engine/): arquitectura y referencias numéricas de crédito.
7. [Riesgo corporativo y construcción](07-financial-and-construction-risk-lab/): baselines Python/C++, experimentos y 45 carpetas preservadas con solapamientos documentados.

Los proyectos ejecutables de las dos primeras áreas incluyen notebooks; IFRS 9 conserva su notebook dentro de `notebooks/`. Los diseños de investigación no se cuentan como implementaciones. Los productos en C++ están en [04 · risk-engines](../04-quant-strategy-and-products/risk-engines/).

## Agenda de investigación avanzada — siete proyectos

1. [Originación causal y aprobación contrafactual](04-advanced-research/01-causal-origination-policy/): Estimar el valor causal de aprobar, rechazar o cambiar límite y precio.
2. [Gemelo digital de portafolio y cambios de régimen](04-advanced-research/02-nonstationary-credit-digital-twin/): Anticipar transiciones de estabilidad a fragilidad y evaluar acciones de contención.
3. [Cobranzas causales y políticas dinámicas](04-advanced-research/03-collections-dynamic-treatment-regimes/): Optimizar canal, momento e intensidad de contacto para recuperar valor neto.
4. [IFRS 9: ECL prospectiva y SICR dinámico](04-advanced-research/04-ifrs9-forward-looking-ecl/): Estimar pérdidas 12m y lifetime consistentes con supervivencia, macro y staging.
5. [SIAR: contagio entre crédito, liquidez, mercado y operación](04-advanced-research/05-siar-integrated-risk-contagion/): Cuantificar amplificación conjunta de shocks y vulnerabilidades de cartera.
6. [Originación MCA con flujos comerciales intermitentes](04-advanced-research/06-mca-cashflow-credit-underwriting/): Inferir capacidad de pago bajo ventas irregulares y datos escasos.
7. [Optimización de portafolio con capital y provisiones](04-advanced-research/07-capital-constrained-portfolio-control/): Asignar originación, pricing y límites maximizando valor sujeto a ECL y capital.

**Estado:** propuestas metodológicas, no implementaciones ni resultados empíricos. Cada proyecto incluye formulación, identificación, validación, arquitectura objetivo y gobierno.

## Enterprise Risk Advisory — consultoría integral

[56 proyectos especificados en ocho líneas de servicio](05-enterprise-risk-advisory/). Incluyen gobierno, capital, liquidez, operacional, resiliencia, ciber, IA, fraude, cumplimiento, seguros, clima, contraparte, controles y datos de riesgo. **Diseños metodológicos pendientes de implementación.**


## Cobertura: regulación prudencial, gestión integral y continuidad

**Competencia objetivo:** gestión integral de riesgos, capital y resiliencia: Basilea III y sus reformas finales (habitualmente denominadas Basilea IV), activos ponderados por riesgo (RWA), revisión supervisora (SREP), evaluación interna de suficiencia de capital y liquidez (ICAAP/ILAAP), ISO 31000, COSO ERM, continuidad del negocio (BCP) e indicadores clave de riesgo (KRIs).

Esta matriz amplía el alcance de investigación del portafolio. Las conexiones señalan proyectos relacionados; no acreditan implementaciones completas, certificaciones ni experiencia operativa con cada marco.

| Tema | Conexión con el portafolio | Desarrollo y evidencia pendientes |
|---|---|---|
| Basilea III y reformas finales / Basilea IV | Enterprise Risk Advisory; riesgo de crédito, mercado y operación | Mapa de requisitos por jurisdicción y versión, cálculo reproducible y conciliación de capital |
| RWA | Crédito y optimización de cartera con restricciones de capital | Motor de RWA con exposiciones, clasificación, ponderaciones, mitigantes, trazabilidad y pruebas de reconciliación |
| SREP | Gobierno, apetito de riesgo y reportes ejecutivos | Expediente de revisión supervisora, matriz de hallazgos, evidencia y seguimiento de acciones |
| ICAAP | Capital, estrés integrado y asignación de recursos | Evaluación de riesgos materiales, proyección de capital, escenarios y acciones de gestión |
| ILAAP | Liquidez, fondeo, balance y resiliencia | Proyecciones de liquidez, estrés, capacidad de respuesta y plan de contingencia de fondeo |
| ISO 31000 | Gobierno y evaluación integral de riesgos | Mapa de principios, proceso, responsables y evidencia de aplicación |
| COSO ERM | Estrategia, apetito de riesgo y control de gestión | Relación entre objetivos, riesgos, respuestas, desempeño y supervisión |
| BCP | Resiliencia y planificación de recuperación | Análisis de impacto de negocio, dependencias críticas, objetivos de recuperación y ejercicios documentados |
| KRIs | Apetito de riesgo y reportes al comité/consejo | Diccionario de indicadores, fórmulas, fuentes, periodicidad, umbrales, responsables y escalamiento |

**Estado al 10 de noviembre de 2026:** cobertura temática parcial; verificación específica e implementación pendientes por marco. Cada avance debe adjuntar código o documentación verificable, datos y supuestos, pruebas y limitaciones. Los ejercicios de capital y liquidez deben distinguir métricas regulatorias de aproximaciones de investigación y de provisiones IFRS 9.

Antes de implementar requisitos regulatorios se documentarán la fuente oficial, la versión vigente, la jurisdicción y el tipo de entidad. SREP, ICAAP e ILAAP se estudiarán con su contexto supervisor; su inclusión no presupone aplicación automática en Colombia.

## Revisión técnica de riesgo — 18 de octubre de 2026 UTC

La [revisión y evidencia](REVIEW_2026-10-18.md) registra errores reproducidos, cambios de contrato, cobertura y límites. Incluye:

- Corrección de ES en construcción y alineación de VaR/ES Python/C++/mercado-liquidez.
- Contratos de datos para ECL, pesos de escenario y validación de PD.
- Stage 3 financiado con recuperaciones esperadas explícitas, separado de la aproximación de default futuro de Stage 1/2.
- [Notebook de mercado y financiación](03-market-liquidity-research/notebook.ipynb) y [notebook de construcción](07-financial-and-construction-risk-lab/notebook.ipynb).

No se elevan los diseños a productos ni se certifica implementación contable o prudencial completa.
