# Causal attribution of delays

**Maturity:** research specification, not a calibrated implementation.

## Research question
DAG-informed treatment effect of contractor interventions on delivery. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
ATE=E[Y(1)-Y(0)]
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**
