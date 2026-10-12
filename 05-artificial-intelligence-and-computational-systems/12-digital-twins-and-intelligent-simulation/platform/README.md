# Economic & Innovation Digital Twin Platform

**Shared design architecture (S1).** Composes financial, macro, micro, innovation and policy twins through typed state/flow interfaces, a common event clock and reproducible scenario experiments. No runnable engine is claimed.

## Logical architecture

```text
Licensed Public Data / Authorized Institution Data / Synthetic Fixtures
            ↓
Point-in-time Ingestion → Provenance → Versioned Observations
            ↓
Economic Ontology + Units + Stock-Flow Accounting + Agent Registry
            ↓
State Estimation / Econometric Calibration / Bayesian Assimilation
            ↓
Scenario & Intervention Registry (time, location, policy, uncertainty)
            ↓
Simulation Kernel / Agent Runtime / Equilibrium Solver / Graph Engine
            ↓
Coupling Layer: banking ↔ firms ↔ households ↔ labor ↔ technology ↔ policy
            ↓
Forecasts + Distributional Outcomes + Welfare + Risk + Fiscal Impact
            ↓
Model Validation → Independent Challenge → Decision Evidence / Reports
```

## Domain boundary and time semantics

Each twin publishes state variables, stocks, flows, units, frequency, geography, entity level, uncertainty, availability time and valid intervention assumptions. A daily banking twin cannot be directly joined to quarterly GDP without explicit aggregation/interpolation, measurement equation and uncertainty. Coupled simulations use an event calendar, lagged feedback or a documented simultaneous solver; no silent circular update.

## Modules (proposed, not yet created)

`ingestion/`, `ontology/`, `state-estimation/`, `simulation/`, `coupling/`, `scenario-engine/`, `policy-evaluation/`, `validation/`, `observability/`, `api/`, `security/`.

## Deployment tiers

Research local (public data); batch analytical (periodic snapshots); institution tactical (authorized data, D+1); near-real-time only when appropriate event feeds exist. All high-impact decisions remain subject to policy controls and review.

[Architecture details](ARCHITECTURE.md) · [Data contracts](CONTRACTS.md) · [Research protocol](RESEARCH_AND_VALIDATION.md) · [Economics foundations](../fundamentals/04-economic-theory-and-identification.md).
