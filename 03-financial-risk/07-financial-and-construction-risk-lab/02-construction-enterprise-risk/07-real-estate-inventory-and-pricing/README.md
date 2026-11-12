# Real estate inventory and pricing

**Maturity:** research specification, not a calibrated implementation.

The [CEED DANE supply-flow companion](observed-dane-ceed-housing-supply-flow/README.md) adds observed quarterly starts and completions by VIS/No VIS through 2026-II. The separate [completed unsold stock companion](observed-dane-ceed-unsold-completed-stock/README.md) processes DANE's published quarterly stock of completed housing units unsold for sale (2020-III–2026-II; 23 coverage areas). This is a real public inventory indicator, but it does not measure presales, total inventory under construction, time-on-market, sales absorption, price elasticity or project-level outcomes. Those remain data gaps for decisions about a specific development.

## Research question
Unsold units, time-on-market, price elasticity and discount policy. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
Revenue=sum_i units_i*price_i*conversion_i
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**
