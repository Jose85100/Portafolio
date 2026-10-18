# Financial Risk Research

Crédito, mercado, liquidez, riesgo sistémico, IFRS 9 y stress testing integrado. Investigación y productos sujetos a validación empírica.

## Estructura

1. [Crédito](01-credit-risk/): [productos de crédito](01-credit-risk/credit-risk-products/) y [estrategia de cartera](01-credit-risk/credit-portfolio-strategy/): scoring, IFRS 9, cosechas, concentración, cópula, capital y apetito de riesgo.
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


## Revisión técnica de riesgo — 18 de octubre de 2026 UTC

La [revisión y evidencia](REVIEW_2026-10-18.md) registra errores reproducidos, cambios de contrato, cobertura y límites. Incluye:

- Corrección de ES en construcción y alineación de VaR/ES Python/C++/mercado-liquidez.
- Contratos de datos para ECL, pesos de escenario y validación de PD.
- Stage 3 financiado con recuperaciones esperadas explícitas, separado de la aproximación de default futuro de Stage 1/2.
- [Notebook de mercado y financiación](03-market-liquidity-research/notebook.ipynb) y [notebook de construcción](07-financial-and-construction-risk-lab/notebook.ipynb).

No se elevan los diseños a productos ni se certifica implementación contable o prudencial completa.

### IFRS 9 multimodelo

La [plataforma de impairment](01-credit-risk/credit-risk-products/ifrs9-investigacion-cuantitativa/README.md) incluye 3 PD, 3 LGD, exposición contractual/CPR/CCF, Stage 3 por recuperaciones y matriz simplificada. Cuatro notebooks nuevos comparan 18 configuraciones bajo datos sintéticos; los modelos no se consideran validados externamente.
