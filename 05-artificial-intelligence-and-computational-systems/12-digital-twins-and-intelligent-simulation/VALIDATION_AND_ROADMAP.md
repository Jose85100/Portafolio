# Validation protocol and phased roadmap

## Research questions

H1: State assimilation improves out-of-time forecasts vs frozen deterministic baseline.
H2: Coupled twins detect more joint threshold breaches under coherent stress than independent models.
H3: Policy-conditional scenarios improve risk-adjusted decisions net of implementation cost **only if** the policy effect is identifiable or explicitly simulated under structural assumptions.

These are **hypotheses**, not verified findings.

## Baselines and evaluation matrix

| Component | Baseline | Advanced candidate | Main validation |
|---|---|---|---|
| Banking | deterministic balance-sheet waterfall | behavioral deposit/credit feedback | reconciliation, runoff calibration |
| Payments | FIFO deterministic queue | stochastic priority + liquidity scheduling | p99 delay, settled value, replay |
| Credit | homogeneous Markov / survival | hierarchical multi-state state-space | OOT calibration, cashflow errors |
| Liquidity | contractual cash ladder | stochastic correlated runoff | shortfall coverage, reverse stress |
| Fraud | static rules | temporal graph + adaptive game | precision at capacity, friction |
| Operations | independent availability | dependency cascade | outage loss, recovery quantiles |
| Integrated | independent silo shocks | coupled propagation | joint tail breaches, attribution |

## Model risk and validation gates

**S0 scope:** decision owner, authorized data, literature, legal/compliance perimeter.

**S1 theory:** derivations, assumptions, invariants, counterexamples, uncertainty decomposition.

**S2 reference implementation:** Python baseline, C++20 kernel if warranted, tests, seeded fixtures, CI.

**S3 empirical validation:** rolling-origin split, independent holdout, bootstrap/block bootstrap, uncertainty calibration, sensitivity, realistic stress.

**S4 challenger review:** independent model validation, accounting reconciliation, performance, cyber/privacy review, reproducibility package.

**S5 governed operation:** shadow mode, monitoring, override policy, model registry, rollback, periodic review and incident response.

## Indicative order and effort

Phase A (4–6 weeks): contracts, synthetic event generator, cashflow ledger and deterministic payment queue. Phase B (6–10 weeks): credit and liquidity baselines, state assimilation, out-of-time validation. Phase C (8–12 weeks): operational dependencies and payment-network stress. Phase D (8–16 weeks): coupled simulation, reverse stress and independent review. These are rough **single-developer research estimates** assuming access to usable data; institutional validation and integrations can take substantially longer.

## Use in a digital bank

- Daily: update deposit runoff, credit migration and funding state from D+1 ledger snapshots; simulate next 7/30/90 days and escalate threshold breaches.
- Intraday (only with approved event feeds): update settlement queues, payment rail availability and liquidity buffers; prioritize incident response, never autonomously move funds without approved controls.
- Weekly: stress coherent combinations of macro shock, fraud surge, processor outage and accelerated withdrawals.
- Monthly: compare model forecasts with actuals, recalibrate, report model risk and economic impact.

## Public-data path

Start with publicly licensed macro time series, central-bank payment reports, bank aggregate financial statements and documented synthetic ledgers. Avoid inventing real-time participant data, fraud labels or borrower-level outcomes. A public-data demonstration is a research prototype, not a validated bank twin.
