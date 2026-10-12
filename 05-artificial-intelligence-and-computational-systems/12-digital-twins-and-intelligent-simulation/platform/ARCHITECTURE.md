# Technical architecture, coupling and orchestration

## 1. Six bounded contexts

**Finance:** balances, credit transitions, payment finality, liquidity. **Macro:** sectoral accounts, prices, output, monetary policy. **Micro:** household/firm choice, competition and market clearing. **Innovation:** adoption, task automation, R&D and knowledge spillovers. **Public policy:** tax/transfer, education, health and energy. **Integration:** multi-domain propagation and welfare/risk reporting.

## 2. Components and interfaces

1. `ObservationIngestor` validates units, vintage, license, availability time, schema and provenance.
2. `StateEstimator` maps observed variables to latent state with posterior covariance/particles.
3. `AgentRegistry` maps pseudonymous agents and economic sectors with typed attributes and lifecycle.
4. `ScenarioRegistry` stores baseline, exogenous shocks, interventions, horizon and assumptions.
5. `SimulationKernel` advances state and writes immutable event log; separate discrete-event and fixed-step engines.
6. `CouplingAdapter` transforms outputs to inputs with declared time aggregation, unit conversions, feedback lag and uncertainty.
7. `PolicyEvaluator` computes welfare, distribution, financial stability and budget constraints; causal estimates require identification.
8. `ValidationEngine` runs accounting, holdout, sensitivity, convergence, ablation and fairness checks.

## 3. Coupling example: AI adoption → labor → demand → credit

```text
Firm AI adoption (task automation + complementary capital)
 → sector productivity and labor demand
 → occupational wages, transitions, household disposable income
 → consumption and firm sales
 → merchant cashflow and loan repayment
 → bank credit loss / liquidity / pricing
 → financing conditions and subsequent technology adoption
```

All transitions are **hypotheses with calibrated parameters**, not empirical facts. For simultaneous feedback, define x*=F(x*;θ,z) and establish convergence conditions (e.g. contraction under suitable norm) or use robust nonlinear solver with diagnostics. If multiple equilibria exist, report scenario-dependent equilibrium selection rather than one unique forecast.

## 4. Economic consistency

Require household + firm + government + rest-of-world sector financial balances sum to zero under consistent conventions. Trade flows obey country-sector accounting identities. For transfers, distinguish real resources from financial claims. Employment transitions preserve population stocks after explicitly modeled entry/exit. Technology adoption cannot increase output mechanically without production assumptions and costs.

## 5. Distributed execution

Use job DAGs for calibration → baseline → shocks → replications → validation → report. Each job has run_id, scenario_id, model version, seed, input hashes, dependency status, deadline and retry policy. C++20 only for profiled heavy kernels; Python orchestration, typed APIs and SQL/Parquet data storage. Event-sourcing and idempotent writes; no false exactly-once guarantee for external effects.

## 6. Threat model and governance

Risks: misleading policy inference, sensitive microdata leakage, uncontrolled automated decisions, corrupted public revisions, malicious dependency updates and false precision. Controls: least privilege, secrets outside repo, provenance, versioned model cards, independent review, stress scenarios, rollback and transparent limits.
