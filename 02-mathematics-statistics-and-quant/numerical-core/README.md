# Numerical Core — reproducible mathematical kernels

**Status: M1–M2 partial.** Dependency-free Python implementations and deterministic numerical tests. These are explicitly **not** implementations of all 20 advanced research programs.

## Contract and assumptions
- `quantile`: nearest-rank empirical quantile; discrete finite-sample convention.
- `expected_shortfall`: average observations from the VaR order-statistic index onward; not a universally unique discrete ES convention.
- `wasserstein_1d`: exact empirical W1 **only for equal sample sizes and uniform weights**. Sort-and-pair proof follows the monotone optimal coupling in one dimension.
- `kl_bernoulli`: KL divergence with exact boundary conventions; Gibbs inequality implies nonnegativity.
- `euler_maruyama_gbm`: explicit Euler scheme for dS=mu S dt + sigma S dW. Coarse steps can produce negative states. Deterministic sigma=0 has first-order global convergence. For sigma>0, classical strong order 1/2 requires regularity assumptions and is not established by a single-seed experiment.
- `bs_call`: European call under risk-neutral lognormal model, no dividends, constant r and sigma.
- `mc_call`: independent exact-GBM samples; unbiased payoff mean, estimated standard error using sample variance; confidence checks are stochastic and not proof of calibration.

## Mathematical verification
For sigma=0: Euler approximation `S_n=S_0(1+mu*T/n)^n`, converges to `S_0 exp(mu*T)`. Error is O(1/n) for fixed mu,T. The benchmark verifies monotone error reduction for a positive drift.

For a call: `C=S_0 Phi(d1)-K exp(-rT) Phi(d2)`. Monte Carlo discounts exact risk-neutral terminal payoffs. Under finite payoff variance, CLT yields asymptotic uncertainty `SE=s/sqrt(N)`. The fixed-seed 4-SE gate is a smoke test, not a guarantee of distributional accuracy.

## Reproduce
From repo root:
```bash
python -m unittest discover -s 02-mathematics-statistics-and-quant/numerical-core/tests -p 'test_*.py' -v
python 02-mathematics-statistics-and-quant/numerical-core/benchmarks/convergence.py
python 02-mathematics-statistics-and-quant/numerical-core/scripts/repository_inventory.py
```

## Limitations and next steps
No empirical calibration, cross-language parity, multidimensional optimal transport, jump diffusion, sensitivity adjoints, uncertainty propagation or independent validation. Add property-based tests, CI performance budgets, benchmarks against SciPy/QuantLib and independent peer review before promotion to M2 across all kernels.


## Notebook de la revisión semanal

[Experimentos ejecutados](notebook.ipynb): Convergencia fuerte de GBM con ruido acoplado, error Monte Carlo y convenciones de ES.
