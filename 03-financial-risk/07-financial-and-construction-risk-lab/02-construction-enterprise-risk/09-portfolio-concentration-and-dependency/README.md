# Project portfolio concentration and dependency

**Maturity:** research specification, not a calibrated implementation.

## Public observed context

The [DNP/SGR concentration companion](../11-portfolio-project-concentration/observed-dnp-sgr-project-concentration/README.md) describes the distribution of reported public-investment value by sector, department and executing entity. It provides an observed baseline for concentration diagnostics, but it does not identify dependencies or losses across projects and cannot calibrate this portfolio model.

## Research question
Copula and shared factor project losses, diversification and tail concentration. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
L_port=sum_i w_i*L_i; ES_alpha=E[L_port | L_port>=VaR_alpha]
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**
