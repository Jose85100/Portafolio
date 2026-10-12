# Credit Portfolio & Collections Twin

**Status:** S1 specification; no tested model or bank-specific validation is claimed.

## 1. Problem, use cases and decision boundary

**Focus:** Credit states, cashflows, prepayment, collections and loss.

**Research question:** Can dynamic borrower/merchant states improve forecasted losses and evaluate collections intensity under macro shocks?

**Business decisions:** identify a risk/operations decision, owner, horizon, feasible interventions and forbidden automated actions. Keep human approval for material credit, liquidity, payment or compliance changes.

## 2. Formal mathematical model

State S_i∈{current,delinquent,default,cured,closed}; P(S_i[t+1]=j|S_i[t]=k,Z_t,U_i[t]); loss=Σ 1_default·LGD·EAD; recoveries follow dated cashflow processes.

For each state define dimensional units, accounting mapping, horizon, conditioning information, stochastic innovations and explicit domain constraints. Establish probability normalization, balance conservation, monotonicity or counterexamples, and when solution uniqueness/stability can fail. Distinguish physical dynamics from observational proxies.

## 3. Statistical model and identification

Multi-state survival and hidden semi-Markov; cure/prepay competing risks; hierarchical LGD, exposure paths and vintage dependence.

Declare likelihood, estimand, censoring, dependence, selection, timestamp availability and regime sensitivity. Parameter estimation must include uncertainty and out-of-time validation. Counterfactual policy comparisons require identification or must be labeled hypothetical.

## 4. Data and access

Public portfolio aggregates and macro data for aggregate stress; loan snapshots, schedules and recoveries require institution access.

Minimum contract: entity_id (pseudonymous), event_time, available_time, state, units, currency when monetary, lineage, source, quality flag and permission. Public data support proof-of-method, not private operational validation.

## 5. Simulation and numerical design

Use Python for calibration/assimilation, C++20 for event-driven simulation or heavy kernels where justified, SQL for point-in-time state and event log. Markov transition baseline vs state-space model; point-in-time backtest and policy ablation.

Run common-random-number scenario comparisons where valid; verify reproducibility, deterministic replay, numerical tolerance, resource use and error handling.

## 6. Evaluation and governance

**KPIs:** PD horizon calibration, EL and tail loss, cure rate, collection cost, recovery NPV and uncertainty bands.

Tests: analytical invariant fixtures, unit and integration, leakage, drift, stress, reverse stress, sensitivity, uncertainty coverage, security and failure injection. Compare against simple baselines with confidence intervals and economics net of operational costs. Track model version, scenario hash, seed and reviewer.

## 7. Key limitations

Collections treatment selection is endogenous; never interpret simulated treatment uplift as causal without identification.

## 8. Delivery gates

G0 literature + scope → G1 mathematical derivation and data contracts → G2 executable baseline/tests → G3 calibration and assimilation → G4 stress and independent validation → G5 shadow deployment and monitored decision support. G2–G5 pending.

[Shared mathematical foundations](../../fundamentals/01-mathematical-foundations.md) · [Statistical foundations](../../fundamentals/02-statistical-foundations.md) · [Computational foundations](../../fundamentals/03-computational-foundations.md).
