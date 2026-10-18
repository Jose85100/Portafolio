# Model catalog and maturity

The lab preserves **45 project directories**: 10 corporate, 21 construction and 14 research. Earlier counts of 22 or 32 described previous catalog versions. Several directories overlap thematically; this is a directory inventory, not 45 independent implemented models. The [CSV inventory](PROJECT_INVENTORY.csv) records each path and the presence of local executable code.

## Executable baselines
- Python: empirical VaR/ES, DSCR/LLCR, CPM critical path, triangular-duration Monte Carlo, Gaussian one-factor credit losses, stochastic project cash-flow shortfall.
- C++17: empirical VaR/ES, deterministic cash path and peak liquidity shortfall.

No empirical calibration, out-of-time validation, or independent model review has been performed.

## Reproducibility
Run from repository root:

```bash
python -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab/python/tests -p 'test_*.py' -v
python -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/01-project-cashflow-at-risk/tests -p 'test_*.py' -v
cmake -S 03-financial-risk/07-financial-and-construction-risk-lab/cpp -B build/construction-risk
cmake --build build/construction-risk
ctest --test-dir build/construction-risk --output-on-failure
```

## Validation roadmap
Dataset contracts; as-of leakage controls; scenario-factor dependence; parameter uncertainty; numerical convergence; out-of-time backtesting; independent validation; risk appetite limits and governance.


## Tail convention and invalid inputs
Nearest-rank empirical VaR is kept; ES now integrates exactly 1−alpha probability mass, fractionally at the boundary atom. This is a deliberate output change from the former rank-inclusive mean. A rational hinge oracle generated 100 shared fixtures. C++ tests throw on failure even when compiled with NDEBUG/Release; prior assert-only checks could be compiled out.

Project finance permits negative CFADS and nonnegative debt service. Zero service has no DSCR; zero debt has no LLCR. Nonfinite cash flows, debt, rates, durations and simulation inputs are rejected. Parameter estimation, recovery models and empirical dependence calibration remain outside these baselines.
