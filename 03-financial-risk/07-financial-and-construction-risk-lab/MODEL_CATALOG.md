# Model catalog and maturity

The lab contains **22 research projects**. Most project directories are research specifications, not working software.

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
