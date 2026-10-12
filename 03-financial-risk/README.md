# Financial Risk Research

Crédito, mercado, liquidez, riesgo sistémico, IFRS 9 y stress testing integrado. Investigación y productos sujetos a validación empírica.

## Contenido

- [Credit risk products](credit-risk-products/): cosechas vintage, matrices de transición, PD/LGD/EAD, scorecard WoE, segmentación, e IFRS 9.
- [Credit portfolio strategy](credit-portfolio-strategy/): RAROC, concentración HHI, cópula gaussiana, límites de apetito, Vasicek.
- [Market and model risk](market-and-model-risk/): backtesting de VaR, GARCH, pruebas de estrés, validación (PSI/Gini), VaR/ES.
- [Market liquidity research](market-liquidity-research/): ES dinámico y EVT, regímenes de volatilidad, liquidez estocástica, espirales de liquidez y optimización de liquidez.

Cada proyecto de las tres primeras carpetas trae un `notebook.ipynb` extenso. Los productos en C++ están en [04 · risk-engines](../04-quant-strategy-and-products/risk-engines/).

## Agenda de investigación avanzada — siete proyectos

1. [Originación causal y aprobación contrafactual](01-causal-origination-policy/): Estimar el valor causal de aprobar, rechazar o cambiar límite y precio.
2. [Gemelo digital de portafolio y cambios de régimen](02-nonstationary-credit-digital-twin/): Anticipar transiciones de estabilidad a fragilidad y evaluar acciones de contención.
3. [Cobranzas causales y políticas dinámicas](03-collections-dynamic-treatment-regimes/): Optimizar canal, momento e intensidad de contacto para recuperar valor neto.
4. [IFRS 9: ECL prospectiva y SICR dinámico](04-ifrs9-forward-looking-ecl/): Estimar pérdidas 12m y lifetime consistentes con supervivencia, macro y staging.
5. [SIAR: contagio entre crédito, liquidez, mercado y operación](05-siar-integrated-risk-contagion/): Cuantificar amplificación conjunta de shocks y vulnerabilidades de cartera.
6. [Originación MCA con flujos comerciales intermitentes](06-mca-cashflow-credit-underwriting/): Inferir capacidad de pago bajo ventas irregulares y datos escasos.
7. [Optimización de portafolio con capital y provisiones](07-capital-constrained-portfolio-control/): Asignar originación, pricing y límites maximizando valor sujeto a ECL y capital.

**Estado:** propuestas metodológicas, no implementaciones ni resultados empíricos. Cada proyecto incluye formulación, identificación, validación, arquitectura objetivo y gobierno.
