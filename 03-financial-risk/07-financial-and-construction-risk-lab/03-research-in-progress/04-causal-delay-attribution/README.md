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

## Contexto público observado (no es validación)

El [intervalo entre radicación y acto ANLA](../../02-construction-enterprise-risk/08-permit-regulatory-and-legal-delay/observed-anla-infrastructure-evaluation-actions/README.md) y el [conteo SECOP de suspensiones/reanudaciones](../../02-construction-enterprise-risk/02-schedule-cost-overrun/observed-secop-work-suspensions/README.md) describen procesos administrativos separados. No enlazan intervención, proyecto y fecha real de entrega; no identifican efecto causal de una acción del contratista.

**Estado de madurez:** la propuesta continúa S1; el companion citado aporta contexto observable, pero no implementa ni valida el modelo descrito.
