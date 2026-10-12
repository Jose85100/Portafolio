# II. Statistical foundations — estimation, assimilation and model risk

## State-space inference

Filtering p(x_t|y_1:t) uses prediction ∫p(x_t|x_{t−1})p(x_{t−1}|y_1:t−1)dx_{t−1} and update proportional to p(y_t|x_t)p(x_t|y_1:t−1). Linear Gaussian systems permit Kalman filters; nonlinear systems may use EKF/UKF, ensemble Kalman or sequential Monte Carlo. Check observability, degeneracy, particle impoverishment and state/parameter identifiability. Forecasting error alone does not validate latent states.

## Model families by mechanism

- Deposits: customer-level hazard / survival, hierarchical random effects, competing events, calendar effects and correlated run dynamics.
- Credit: multi-state transitions, discrete hazard, cure, default, prepayment, EAD trajectories, LGD recoveries with censoring and vintage effects.
- Payments: marked point processes, queue arrivals/service, Hawkes self-excitation when justified, intraday seasonality and merchant heterogeneity.
- Fraud: graph-temporal detection, delayed and selective labels, prevalence shift and adversarial adaptation.
- Cyber/operations: reliability graphs, incident hazard, duration/survival, common-cause failures and provider concentration.
- Macro: state-space nowcasting, mixed-frequency regressors, structural scenarios and uncertainty propagation.

## Estimation discipline

Declare estimand, likelihood/moments, missingness, delayed outcomes, label definition, population, sample selection, treatment assignment, cluster structure and timestamp availability. Avoid future-data leakage: record event_time, ingestion_time, available_time, effective_time and vintage. Compare point-in-time vintages, not revised macro series presented as historically known.

For Monte Carlo estimate μ=E[g(X)], sample mean is unbiased for iid draws with integrable g and has standard error σ/√N if finite variance; correlated paths, importance weights or heavy tails require adjusted inference. For rare-event shortfall consider importance sampling with likelihood ratios and effective sample size, or scenario bounds if data are insufficient.

## Validation ladder

1. Ledger/accounting reconciliation, unit and calendar consistency.
2. One-step and multistep out-of-time forecast errors.
3. Calibration: PIT, interval coverage, Brier/log loss where relevant, reliability curves.
4. Stress realism: scenario plausibility, cross-factor coherence, conditional tails.
5. Backtest by institution type, product, merchant cohort, payment rail, region and macro regime.
6. Baselines: historical extrapolation, logistic/Markov, deterministic queue, cashflow waterfall.
7. Ablation: without assimilation, without network, without feedback, without macro shocks.
8. Model-risk challenge: reverse stress, adversarial scenarios, sensitivity and independent review.

## Causal and decision evaluation

Observed collections policy influences later delinquencies; fraud blocks alter observed labels; liquidity controls influence withdrawals. Evaluate interventions with randomized tests where permissible, or explicitly justified causal identification (sequential exchangeability, positivity, no unmodeled interference). Off-policy value estimation requires logged propensities and support overlap. Counterfactual outputs without these assumptions must be labeled scenario simulations, not estimated treatment effects.

## Data access and external validity

Public data (central-bank rates, public supervisory aggregates, macro time series, payment-system reports and public operational incidents) support macro stress, aggregate calibration and engineering demonstrations. They generally do **not** identify customer-level PD/LGD, real-time settlement queues, deposit-run contagion or fraud policy effects. Use synthetic data only for invariants and demonstrations; never claim bank-specific accuracy without authorized institutional records.
