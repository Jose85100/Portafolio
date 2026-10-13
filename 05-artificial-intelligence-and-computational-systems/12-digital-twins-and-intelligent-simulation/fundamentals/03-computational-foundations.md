# III. Computational foundations — digital twin engineering

## Architecture

Use a modular, event-sourced design: ingestion → point-in-time validation → immutable observations → state estimator → scenario engine → simulation workers → policy evaluator → evidence and monitoring. Do not require always-on architecture when source refresh is D+1; define batch tactical twin vs intraday operational twin separately.

## Technology

- Python 3.12+: calibration, filtering, econometrics, experiment orchestration, API and reporting.
- C++20: deterministic event simulation, network clearing, numerical kernels and Monte Carlo when profiling justifies it.
- SQL/PostgreSQL: immutable event log, bitemporal snapshots, account reconciliation, idempotency and audit.
- Parquet/Arrow: versioned analytical data; message brokers optional for high-frequency flows.
- Containers and CI: reproducible builds, unit/integration/property tests, sanitizers, benchmarks and dependency controls.
- Observability: run_id, trace_id, state_version, input hash, model version, scenario hash, seeds and convergence diagnostics.

## Numerical methods and failure modes

Euler–Maruyama has strong order 1/2 and weak order 1 under standard smoothness/Lipschitz assumptions for generic SDEs; jump models, discontinuous coefficients and constrained states require specialized schemes. Discrete-event simulation should preserve ordering and causality under equal timestamps. Deterministic replay requires stable ordering, RNG stream assignment and versioned external observations. Network clearing algorithms require convergence checks and infeasibility diagnostics. Never silently clip negative cashflow or probabilities; validate domains and record transformations.

## Deployment tiers

- **T0 Research:** public/synthetic data, local batch, reproducible scenario notebooks.
- **T1 Tactical:** governed internal D+1 snapshots, overnight filtering, portfolio and liquidity forecasts, analyst approval.
- **T2 Intraday:** authorized payment events and ledgers, event-driven state updates, explicit latency budgets, circuit breakers.
- **T3 Decision-support:** shadow mode, independent model validation, human sign-off for high-impact actions, rollback and incident playbooks.

## Contracts

TwinObservation/v1, TwinState/v1, TwinScenario/v1, TwinRun/v1, TwinValidation/v1; schemas in [../DATA_CONTRACTS.md](../DATA_CONTRACTS.md). All monetary amounts have currency, minor units or decimal representation; all times have timezone and clock semantics; no unprotected PII or credentials.

## Acceptance

Each project must provide executable baseline, deterministic fixtures, accounting invariants, backtest, stress and reverse stress, performance measurements, model card, independent review and failure-mode table. Document which components are only designs.
