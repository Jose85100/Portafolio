# Financial Risk — mathematical and computational expansion

## Audited scope and interpretation

The current repository has 5 primary domains, with existing products and subprograms. A request for **seven projects per item** can mean either seven per top-level domain (35), seven per substantive thematic line (potentially hundreds), or seven per every existing leaf project (larger still). Do not claim 259 projects have been created. This document establishes an extensible framework and an implemented initial slice.

## Research design standard for every project

1. Define estimand, time horizon, target population and economic decision.
2. State probability space, filtration, information set, assumptions and units.
3. Derive estimators, identification, asymptotics or finite-sample bounds; include counterexamples.
4. Quantify parameter, sampling, scenario and specification uncertainty.
5. Build C++17/20 computational core for numerically intensive routines; Python for estimation, notebooks and simulation orchestration; SQL for point-in-time data and lineage.
6. Test invariants, conservation identities, extreme values, numerical convergence and adversarial inputs.
7. Compare with baseline, cross-validation respecting time, out-of-distribution stress and reproducibility.
8. Record regulatory scope separately for IFRS 9, SFC, Basel and other jurisdictions.

## Seven candidate projects per top-level domain (35 conceptual slots)

### Credit Risk
1. Dynamic competing-risks PD and cure models
2. Stochastic LGD with collateral and recovery delays
3. Behavioral EAD and credit-line utilization
4. Copula and factor-dependent portfolio credit loss
5. Causal origination policy evaluation
6. Merchant cash-flow survival under intermittent sales
7. Capital-constrained dynamic credit allocation

### Market & Model Risk
1. Heavy-tail multivariate VaR/ES
2. Volatility regime-switching state-space models
3. Joint VaR/ES backtesting and calibration
4. Model risk via Bayesian model averaging
5. Robust derivatives sensitivity and hedging
6. Liquidity-adjusted market risk
7. Distribution-shift detection and adaptive validation

### Market & Liquidity Research
1. Dynamic EVT and filtered historical simulation
2. Funding liquidity survival and time-to-exhaustion
3. Fire-sale network propagation
4. Market depth and nonlinear price impact
5. Collateral, haircuts and margin-call dynamics
6. Stochastic ALM liquidity optimization
7. Joint market-funding stress scenario generation

### Advanced Research
1. Counterfactual credit approval under selection
2. Nonstationary portfolio digital twin
3. Dynamic treatment regimes for collections
4. Lifetime IFRS 9 ECL with scenario uncertainty
5. Cross-risk contagion across credit, market and liquidity
6. MCA underwriting with intermittent transaction flows
7. Portfolio control under ECL, capital and concentration

### Enterprise Risk Advisory
1. Enterprise risk aggregation and capital allocation
2. ICAAP/ILAAP stochastic scenario integration
3. Operational loss frequency-severity extremes
4. Cyber risk and dependency networks
5. AML/fraud graph statistical inference
6. Climate credit/market transmission stress
7. XVA and counterparty exposure simulation

## Implementation order

**Phase A:** validate C++ deterministic credit loss kernel and Python reference; add CI and formal contracts.

**Phase B:** extend one rigorous executable project in each of the five domains, including theory, tests, and reproducible synthetic benchmarks.

**Phase C:** expand to seven projects per domain (35), then decide whether the user requires seven for every nested item. No project is labeled implemented until its code and tests exist.
