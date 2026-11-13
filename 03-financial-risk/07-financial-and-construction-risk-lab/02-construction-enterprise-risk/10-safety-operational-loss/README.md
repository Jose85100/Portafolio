# Construction operational and safety loss

**Maturity:** research specification, not a calibrated implementation.

## Public observed context

The [Minsalud workplace-safety companion](../09-construction-safety-and-operational-loss/observed-minsalud-workplace-safety/README.md) provides an aggregate construction-sector benchmark for reported accidents and qualified accident deaths. It does not identify project/contractor outcomes, economic severity, downtime or exposure in hours, so it cannot calibrate this loss model.

## Research question
Compound Poisson severity, downtime and extreme-event losses. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
L=sum_{j=1}^N X_j; N~Poisson(lambda)
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**

For observed sectoral context only, see the [Minsalud workplace-safety companion](../09-construction-safety-and-operational-loss/observed-minsalud-workplace-safety/README.md). It does not validate this loss model or provide contractor/project outcomes.
