# Contractor and project network contagion

**Maturity:** research specification, not a calibrated implementation.

## Research question
Graph exposures, cascading disruptions and critical supplier identification. Determine when this model materially improves risk decisions relative to transparent baselines.

## Mathematical specification
```text
x_{t+1}=1{A*x_t+shock_t>threshold}
```
Define units, filtration, timing, risk horizon, exposure at risk and conditional dependence explicitly. Check identification and avoid treating scenario assumptions as estimated parameters.

## Data contract
Project IDs, as-of date, cashflow/event dates, exposures, contract terms, source lineage and historical outcomes. Possible inputs include ERP, contracts, budgets, site reports and public macroeconomic series. Document missingness and reporting delays.

## Estimation and numerical plan
Build a deterministic baseline, then stochastic scenario engine and parameter estimation; compare against empirical benchmarks. Evaluate out-of-time performance, calibration, stress sensitivity, numerical convergence and uncertainty intervals.

## Model risk and acceptance gates
No deployment without independently reproducible inputs, unit and integration tests, documented limitations, backtesting and governance approval. **Status: design only.**

## Contexto público observado (no es validación)

Los [registros de extensión SECOP](../../02-construction-enterprise-risk/04-contractor-counterparty-risk/observed-secop-works-extension-proxy/README.md), el [perfil financiero Supersociedades](../../02-construction-enterprise-risk/04-contractor-counterparty-risk/observed-supersociedades-corporate-financial-proxy/README.md), la [insolvencia agregada](../../01-corporate-financial-risk/06-counterparty-credit-exposure/observed-supersociedades-insolvency-context/README.md) y la [vinculación de garantías a obras](../../02-construction-enterprise-risk/14-surety-performance-bond-risk/README.md) son insumos públicos independientes. No hay aristas proveedor-obra y outcomes enlazados para estimar contagio.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
