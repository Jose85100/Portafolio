# Economic Production Network Twin

**Maturity:** S1 — research specification only; no calibration, production connection or empirically verified findings.

## 1. Research problem and economic contribution

**Falsifiable question:** Which input dependencies amplify supply disruptions and price shocks?

**Unit of analysis:** identify household, firm, region, transaction, institution or economic sector as appropriate. State decision horizon, policy levers, observable outcomes, constraints, stakeholder welfare and competing explanations. Report intended research contribution and explicit null hypothesis.

## 2. Mathematical structure and microfoundations

Leontief IO baseline x=(I−A)^{-1}d; nonlinear capacity-constrained production with inventories and delayed shipments.

Define state x_t, agents i, exogenous shocks z_t, action/policy u_t, information filtration and transition law x_{t+1}=F_θ(x_t,u_t,z_t,ε_t). Derive budget/resource conservation, equilibrium or disequilibrium conditions, fixed-point existence requirements and numerical constraints where relevant. Explain what fails under nonconvexity, strategic feedback, limited rationality or structural change.

## 3. Econometric and statistical identification

Estimate input shares, shock propagation, network concentration, Bayesian uncertainty for missing bilateral links.

Define target estimand and data-generating assumptions; handle simultaneity, selection, heterogeneity, missingness, serial/spatial dependence, instrument validity and measurement error. Separate causal effects from calibrated scenarios. Estimate uncertainty with design-appropriate methods; use temporal and geographic holdouts where applicable.

## 4. Data strategy and reproducibility

DANE supply-use accounts, trade statistics, publicly available sector production.

Document licensing, extraction dates, revisions/vintages, sampling weights, units, privacy and exact data availability time. Synthetic agents/records can test mechanics but cannot establish external validity.

## 5. Engineering architecture

Python 3.12+ for data ingestion, econometrics, calibration and experiments; C++20 for agent-based simulation, numerical kernels or graph propagation **only when profiled**; SQL/Parquet for point-in-time observations; JSON Schema for scenario/state/result contracts. Organize future implementation as `src/`, `models/`, `contracts/`, `tests/`, `experiments/`, `reports/`. Integrate with shared [platform](../../platform/README.md).

## 6. Experiments, baselines and model validation

**Baselines:** no-policy deterministic projection, parsimonious econometric model and simpler behavioral/structural mechanism where appropriate. Compare with advanced candidate under identical data and shocks.

**Metrics:** Output loss, upstream centrality, recovery time, cascade size.

Require conservation/property tests, rolling-origin or out-of-region evaluation, posterior predictive checks where Bayesian, scenario plausibility, stress and reverse stress, Monte Carlo error, sensitivity to behavioral assumptions, computational scaling and independent model review. Pre-register hypotheses before testing.

## 7. Risks and research gates

Risks include Lucas critique, Goodhart effects, network interference, policy endogeneity, weak identification, equilibrium multiplicity, data revisions and institutional mismatch. Explicitly document all. **G0** literature and scope → **G1** formal derivation/data contract → **G2** executable baseline and unit tests → **G3** calibration and uncertainty → **G4** challenger and sensitivity → **G5** controlled use. G2–G5 pending.
