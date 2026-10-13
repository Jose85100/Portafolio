# Fraud & Financial Crime Twin

**Status:** S1 specification; no tested model or bank-specific validation is claimed.

## 1. Problem, use cases and decision boundary

**Focus:** Adaptive fraud attacks, AML alert capacity and customer friction.

**Research question:** How do adaptive attackers and defensive controls interact under payment volume growth and changing fraud prevalence?

**Business decisions:** identify a risk/operations decision, owner, horizon, feasible interventions and forbidden automated actions. Keep human approval for material credit, liquidity, payment or compliance changes.

## 2. Formal mathematical model

Attacker action a_t and defender policy π_t form a stochastic game; objective min_π E[fraud_loss+review_cost+false_block_cost] subject to policy and capacity constraints.

For each state define dimensional units, accounting mapping, horizon, conditioning information, stochastic innovations and explicit domain constraints. Establish probability normalization, balance conservation, monotonicity or counterexamples, and when solution uniqueness/stability can fail. Distinguish physical dynamics from observational proxies.

## 3. Statistical model and identification

Temporal graph anomaly, rare-event prevalence shift, delayed labels, selective review, false-positive burden and adversarial adaptation.

Declare likelihood, estimand, censoring, dependence, selection, timestamp availability and regime sensitivity. Parameter estimation must include uncertainty and out-of-time validation. Counterfactual policy comparisons require identification or must be labeled hypothetical.

## 4. Data and access

Public fraud trend aggregates and synthetic transaction networks; labeled cases and interventions require authorized data.

Minimum contract: entity_id (pseudonymous), event_time, available_time, state, units, currency when monetary, lineage, source, quality flag and permission. Public data support proof-of-method, not private operational validation.

## 5. Simulation and numerical design

Use Python for calibration/assimilation, C++20 for event-driven simulation or heavy kernels where justified, SQL for point-in-time state and event log. Rules baseline vs risk-adaptive prioritization; simulate attacker adaptation and review capacity shocks.

Run common-random-number scenario comparisons where valid; verify reproducibility, deterministic replay, numerical tolerance, resource use and error handling.

## 6. Evaluation and governance

**KPIs:** Fraud loss per transaction, precision at review capacity, customer friction, alert lag, calibration and leakage rate.

Tests: analytical invariant fixtures, unit and integration, leakage, drift, stress, reverse stress, sensitivity, uncertainty coverage, security and failure injection. Compare against simple baselines with confidence intervals and economics net of operational costs. Track model version, scenario hash, seed and reviewer.

## 7. Key limitations

Synthetic attacks cannot establish production detection accuracy; protect sensitive patterns and personal data.

## 8. Delivery gates

G0 literature + scope → G1 mathematical derivation and data contracts → G2 executable baseline/tests → G3 calibration and assimilation → G4 stress and independent validation → G5 shadow deployment and monitored decision support. G2–G5 pending.

[Shared mathematical foundations](../../fundamentals/01-mathematical-foundations.md) · [Statistical foundations](../../fundamentals/02-statistical-foundations.md) · [Computational foundations](../../fundamentals/03-computational-foundations.md).
