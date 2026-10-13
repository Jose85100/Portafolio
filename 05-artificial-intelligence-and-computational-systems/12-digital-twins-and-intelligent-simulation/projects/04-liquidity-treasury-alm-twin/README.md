# Liquidity, Treasury & ALM Twin

**Status:** S1 specification; no tested model or bank-specific validation is claimed.

## 1. Problem, use cases and decision boundary

**Focus:** Liquidity buffers, deposit outflows, collateral, funding and rate shocks.

**Research question:** When do deposit withdrawals and payment settlements create intraday or multi-day funding gaps?

**Business decisions:** identify a risk/operations decision, owner, horizon, feasible interventions and forbidden automated actions. Keep human approval for material credit, liquidity, payment or compliance changes.

## 2. Formal mathematical model

Cash[t+1]=Cash[t]+customer_netflows+funding−settlement_outflows−margin_calls; min_t Cash_t and shortfall paths; EVE=PV(assets)−PV(liabilities).

For each state define dimensional units, accounting mapping, horizon, conditioning information, stochastic innovations and explicit domain constraints. Establish probability normalization, balance conservation, monotonicity or counterexamples, and when solution uniqueness/stability can fail. Distinguish physical dynamics from observational proxies.

## 3. Statistical model and identification

Cashflow-at-risk, correlated runoff, curve scenarios, stochastic rates, liquidity contagion and parameter uncertainty.

Declare likelihood, estimand, censoring, dependence, selection, timestamp availability and regime sensitivity. Parameter estimation must include uncertainty and out-of-time validation. Counterfactual policy comparisons require identification or must be labeled hypothetical.

## 4. Data and access

Public yield curves, liquidity indicators and bank disclosures; intraday balances, collateral and contractual flows require access.

Minimum contract: entity_id (pseudonymous), event_time, available_time, state, units, currency when monetary, lineage, source, quality flag and permission. Public data support proof-of-method, not private operational validation.

## 5. Simulation and numerical design

Use Python for calibration/assimilation, C++20 for event-driven simulation or heavy kernels where justified, SQL for point-in-time state and event log. Deterministic cashflow ladder vs stochastic joint deposit/payment simulation; liquidity and rate shocks.

Run common-random-number scenario comparisons where valid; verify reproducibility, deterministic replay, numerical tolerance, resource use and error handling.

## 6. Evaluation and governance

**KPIs:** Survival horizon, liquidity shortfall probability, peak funding need, EVE/NII shocks and reverse-stress threshold.

Tests: analytical invariant fixtures, unit and integration, leakage, drift, stress, reverse stress, sensitivity, uncertainty coverage, security and failure injection. Compare against simple baselines with confidence intervals and economics net of operational costs. Track model version, scenario hash, seed and reviewer.

## 7. Key limitations

Separate liquidity risk from accounting losses; regulatory LCR/NSFR calculations require actual jurisdiction-specific rules and classifications.

## 8. Delivery gates

G0 literature + scope → G1 mathematical derivation and data contracts → G2 executable baseline/tests → G3 calibration and assimilation → G4 stress and independent validation → G5 shadow deployment and monitored decision support. G2–G5 pending.

[Shared mathematical foundations](../../fundamentals/01-mathematical-foundations.md) · [Statistical foundations](../../fundamentals/02-statistical-foundations.md) · [Computational foundations](../../fundamentals/03-computational-foundations.md).
