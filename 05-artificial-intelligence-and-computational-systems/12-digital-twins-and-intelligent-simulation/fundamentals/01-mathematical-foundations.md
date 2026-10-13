# I. Mathematical foundations — Digital Twins for Banking, Payments & Risk

## 1. What is a twin?

A digital twin is a versioned state estimator plus a calibrated dynamical system, updated with available observations and capable of generating falsifiable forecasts and policy-conditional scenarios. A dashboard, a static Monte Carlo model or a synthetic-data generator alone is **not** a synchronized twin.

Define filtered probability space (Ω,F,(F_t),P), observation sigma-algebra G_t⊆F_t, latent state X_t∈R^d, control U_t, exogenous macro-financial factors Z_t, and observation Y_t. At discrete time:

```text
X[t+1] = f_theta(X[t], U[t], Z[t], W[t])
Y[t]   = h_theta(X[t]) + V[t]
P(X[t+1]|G[t],do(U[t]=u)) is policy-conditional ONLY under structural identification
```

The state is not a ledger balance alone: it may include payment queue length, cash buffers, hazard rates, credit stages, merchant cashflow and provider availability. Specify units, sign conventions and calendar for each coordinate.

## 2. Conservation laws and accounting identities

For an entity-level cash account, at compatible event times and with consistently signed external flows:

```text
cash[t+1] = cash[t] + inflows[t] - outflows[t] + funding[t] - repayments[t] - fees[t]
```

An interbank payment transfers liquidity between participants; aggregate internal transfer flows cancel. Credit cashflow schedules distinguish principal, interest, fees, recoveries, write-offs and undrawn commitments. Deposit withdrawals are bank cash outflows and liability reductions, not automatically accounting losses. Reconcile model state with double-entry postings, settlement ledgers and cut-off rules. Never add overlapping exposures twice.

## 3. Stochastic credit and payments

For borrower i, define default time τ_i and conditional intensity λ_i(t|X_t,Z_t), with survival P(τ_i>t|path)=exp(-∫_0^t λ_i(s)ds) under intensity assumptions. Portfolio loss over horizon H:

```text
L_H = sum_i 1{tau_i <= H} * LGD_i(tau_i) * EAD_i(tau_i)
EL_H = E[L_H]
```

The simplification Σ PD_i×LGD_i×EAD_i requires appropriate conditional or independence assumptions and aligned horizons. Payment queues can be represented by discrete-event systems; M/M/1 formula E[T]=1/(μ−λ) requires Poisson arrivals, exponential service, λ<μ and stationary regime. Use empirical/event simulation for batch settlement, priority queues and correlated bursts.

## 4. Dynamic balance sheet and liquidity

Let B_t denote liquid assets net of operational encumbrance, F_t net funding, C_t net customer/payment cashflow, M_t margin and settlement needs:

```text
B[t+1] = B[t] + F[t] + C[t] - M[t]
LiquidityShortfall_H = max(0, -min_{0<=t<=H} B[t])
```

Separate stock/flow quantities, intraday liquidity from end-of-day liquidity, regulatory ratios from internal operational buffers. A threshold breach is a model outcome, not a regulatory determination without verified jurisdiction-specific definitions.

## 5. Network contagion and fixed points

With obligations matrix Π and external resources e, clearing payments p may satisfy:

```text
p_i = min(bar_p_i, e_i + sum_j Π[j,i] * p_j)
```

This is a stylized clearing system under limited liability, proportional payments and fixed obligations; real payment systems require timing, collateral, priorities and legal settlement finality. Investigate existence and uniqueness, monotone iteration, and when multiple equilibria or feedback invalidate simplistic clearing assumptions.

## 6. Nonlinear state estimation and intervention

Continuous dynamics may use dX_t=μ_θ(X_t,U_t,Z_t)dt+σ_θ(X_t,U_t,Z_t)dW_t; existence/uniqueness requires suitable growth and Lipschitz conditions. Discrete-time regimes and jump processes may be preferable for payment outages and defaults. A simulation under U=u is not a causal effect unless assignment mechanisms, confounding, interference and policy feedback are addressed.

## 7. Required derivations and failure cases

1. Prove accounting conservation and reconciliation invariants.
2. Prove a basic transition kernel preserves probability mass.
3. Derive a stable queue baseline and exhibit instability at λ≥μ.
4. Demonstrate tail dependence sensitivity beyond correlation.
5. Check whether state is observable and structural parameters identifiable.
6. Separate stochastic simulation uncertainty, parameter uncertainty and model-form uncertainty.
7. Document discretization bias, convergence and regime-change counterexamples.
