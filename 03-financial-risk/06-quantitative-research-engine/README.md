# Financial Risk Quantitative Research Engine — first verified vertical slice

**Status:** research-grade foundational implementation; not a regulatory model, production service, IFRS 9 lifetime engine, or validated capital model.

## Mathematical specification

For exposures i=1,…,n, let D_i be Bernoulli(PD_i) and a_i=LGD_i EAD_i, where LGD/EAD are deterministic nonnegative quantities. Define L=Σ_i a_i D_i.

Linearity of expectation gives E[L]=Σ_i a_i PD_i **without assuming independent defaults**.

Variance satisfies Var(L)=Σ_i a_i² PD_i(1−PD_i)+2Σ_{i<j}a_i a_j Cov(D_i,D_j).

The C++ covariance API computes aᵀ C a from a caller-provided covariance matrix C. **It checks shape, symmetry, finiteness and nonnegative portfolio variance, but does not certify that C is PSD or that its entries are compatible with Bernoulli marginals.** Validate those upstream before any risk use.

Under independent defaults, Cov(D_i,D_j)=0 for i≠j, yielding the diagonal formula.

### Assumptions and exclusions

- PD and LGD lie in [0,1]; EAD is nonnegative; horizons must match.
- LGD/EAD are fixed. If stochastic and correlated with default, E[D LGD EAD] need not equal PD × E[LGD] × E[EAD].
- No discounting, time-to-default, survival curves, macroeconomic scenarios, staging, discount-rate conventions, correlation estimation, or tail risk engine.
- Double arithmetic with long-double accumulation, subject to finite-precision limitations.

## Implementation

- `cpp/include/risk/portfolio.hpp`: header-only C++17, deterministic EL and variance.
- `cpp/tests/test_portfolio.cpp`: assertions for baseline values and invalid PD.
- `python/reference.py`: independent reference for EL and independent-default variance.
- `docs/RESEARCH_PROGRAM.md`: domain-level research architecture and phased 7-project expansion framework.

### C++ build and tests

```bash
c++ -std=c++17 -Wall -Wextra -Werror -I cpp/include cpp/tests/test_portfolio.cpp -o /tmp/test_portfolio
/tmp/test_portfolio
```

The C++ kernel was compiled and its assertions executed locally before opening the PR. It is not yet integrated with the existing credit-risk contracts or CI.

## Scientific validation backlog

1. Add a PSD and Bernoulli-feasibility validator for supplied covariance matrices.
2. Test random portfolios against an independent high-precision implementation.
3. Add stochastic LGD/EAD and dependence via Gaussian/t copulas with explicit limitations.
4. Implement lifetime ECL separately with survival, scenarios and discounting.
5. Compare Monte Carlo, quadrature and analytic methods; report error and runtime.
6. Add CI, sanitizers, benchmarks and model governance artifacts.
