# Bayesian project early warning

**Maturity:** research specification, not a calibrated implementation.

## Research question
Hierarchical deterioration indicators with partial pooling across sites. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
logit(P(default_i))=alpha_group+beta'X_i
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**

## Contexto público observado (no es validación)

El [inventario CEED](../../02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-unsold-completed-stock/README.md), el [flujo CEED](../../02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-housing-supply-flow/README.md), el [licenciamiento ELIC](../../02-construction-enterprise-risk/03-presales-demand-and-cancellations/observed-dane-elic-supply-signal/README.md) y las [filas agregadas SECOP de suspensión](../../02-construction-enterprise-risk/02-schedule-cost-overrun/observed-secop-work-suspensions/README.md) son señales contextuales, sin target de deterioro o default por proyecto. No constituyen indicadores de alerta calibrados ni backtest.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
