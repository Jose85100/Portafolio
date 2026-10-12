# Digital Banking System Twin

**Status:** S1 specification; no tested model or bank-specific validation is claimed.

## 1. Problem, use cases and decision boundary

**Focus:** Digital bank economics, deposit behavior and balance-sheet feedback.

**Research question:** Can joint deposit, origination, credit, payment and pricing policies improve risk-adjusted unit economics without breaching funding or operational limits?

**Business decisions:** identify a risk/operations decision, owner, horizon, feasible interventions and forbidden automated actions. Keep human approval for material credit, liquidity, payment or compliance changes.

## 2. Formal mathematical model

Deposits D[t+1]=D[t]+new_funding−withdrawals+accrued_interest; equity E[t+1]=E[t]+net_income−losses−distributions. Behavioral deposit hazards depend on pricing, service incidents and macro factors.

For each state define dimensional units, accounting mapping, horizon, conditioning information, stochastic innovations and explicit domain constraints. Establish probability normalization, balance conservation, monotonicity or counterexamples, and when solution uniqueness/stability can fail. Distinguish physical dynamics from observational proxies.

## 3. Statistical model and identification

Hierarchical deposit survival; customer-product transitions; dynamic balance-sheet accounting; competing-risk closures.

Declare likelihood, estimand, censoring, dependence, selection, timestamp availability and regime sensitivity. Parameter estimation must include uncertainty and out-of-time validation. Counterfactual policy comparisons require identification or must be labeled hypothetical.

## 4. Data and access

Bank-level balance sheet, public rate curves, supervisory aggregates; account-level transactions and attrition only with permission.

Minimum contract: entity_id (pseudonymous), event_time, available_time, state, units, currency when monetary, lineage, source, quality flag and permission. Public data support proof-of-method, not private operational validation.

## 5. Simulation and numerical design

Use Python for calibration/assimilation, C++20 for event-driven simulation or heavy kernels where justified, SQL for point-in-time state and event log. Deterministic balance-sheet waterfall vs deposit hazard + feedback; tests for conservation, bank run shock and repricing.

Run common-random-number scenario comparisons where valid; verify reproducibility, deterministic replay, numerical tolerance, resource use and error handling.

## 6. Evaluation and governance

**KPIs:** Deposit runoff calibration, funding gap, NIM sensitivity, economic capital, risk-adjusted contribution margin.

Tests: analytical invariant fixtures, unit and integration, leakage, drift, stress, reverse stress, sensitivity, uncertainty coverage, security and failure injection. Compare against simple baselines with confidence intervals and economics net of operational costs. Track model version, scenario hash, seed and reviewer.

## 7. Key limitations

Deposit attrition response to competitor rates is observationally confounded; treat policy effects as scenarios absent identification.

## 8. Delivery gates

G0 literature + scope → G1 mathematical derivation and data contracts → G2 executable baseline/tests → G3 calibration and assimilation → G4 stress and independent validation → G5 shadow deployment and monitored decision support. G2–G5 pending.

[Shared mathematical foundations](../../fundamentals/01-mathematical-foundations.md) · [Statistical foundations](../../fundamentals/02-statistical-foundations.md) · [Computational foundations](../../fundamentals/03-computational-foundations.md).
