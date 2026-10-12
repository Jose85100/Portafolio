# Research methodology and validation program

## Formal protocol for each twin

1. Define research question, economic mechanism, competing hypotheses, estimand, welfare metric and policy horizon.
2. Map literature and model alternatives; maintain references with DOI/URLs, edition and known limitations.
3. Specify structural equations, state space, agents, budgets, transition kernels and conditions for existence/identification.
4. Establish point-in-time data catalog, sampling design, spatial and temporal resolution, weights, missingness and revisions.
5. Build an analytically tractable baseline, then advanced model, using identical data and scenario seeds.
6. Validate forecasts out of time, distributional fit, cross-region transfer, sensitivity, structural breaks and uncertainty.
7. Perform counterfactual experiments only when structural/causal assumptions are explicit and defensible.
8. Independently challenge with simpler models, falsification tests, alternative identification, stress and reverse stress.
9. Produce reproducible evidence manifest, economic impact statement, model card, ethics/privacy and governance signoff.

## Statistical pitfalls

Lucas critique, endogenous adoption, simultaneous price determination, spillover/interference, omitted network links, weak instruments, selective participation, macro series revisions, nonstationary equilibrium, survivorship and policy feedback. For policy effects, state positivity, exchangeability and consistency assumptions; ABM mechanism sensitivity is not a causal estimator by itself.

## Metrics by domain

Macro: RMSE/CRPS, sector reconciliation, impulse-response coverage. Micro: likelihood, elasticity uncertainty, consumer surplus. Innovation: adoption hazard calibration, network spillovers, TFP sensitivity. Policy: fiscal incidence, welfare distribution, targeting and uncertainty. Integrated: accounting closure, joint risk, scenario stability and simulation error.

## Monte Carlo

For iid simulation g(X), estimator μhat=N^-1Σg(X_i) has variance Var(g)/N under finite variance. Agent simulations may be dependent and require replicated independent RNG streams, batch means or dependence-aware inference. For rare events, report effective sample size and weight variance; avoid overclaiming precision from a few stress paths.

## Readiness gates

S1 theoretical specification (current) → S2 executable synthetic baseline → S3 calibrated public-data research prototype → S4 independently validated multi-domain experiment → S5 authorized institution/decision-support deployment. S1 does not imply S2 or S3.

## Priority experiment

**AI transformation chain:** compare (A) exogenous productivity shock, (B) endogenous adoption with heterogeneous firms, (C) adoption plus labor-market reallocation and (D) coupled credit/payment feedback. Evaluate distributional outcomes and sectoral accounting, not only aggregate GDP.
