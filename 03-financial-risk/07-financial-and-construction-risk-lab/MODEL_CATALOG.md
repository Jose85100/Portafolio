# Model catalog and maturity

13 new project research specifications complement the existing nine, for **22 research projects** in this lab.

## Implemented baselines
- Python: empirical VaR/ES, DSCR/LLCR, CPM critical path, triangular-duration Monte Carlo, Gaussian one-factor credit losses.
- C++17: empirical VaR/ES, deterministic cash path and peak liquidity shortfall.
- Existing Python: stochastic project cash-flow shortfall engine.

These are **algorithmic baselines**, not full implementations of all 22 project proposals. There is no empirical calibration, out-of-time validation or independent model review.

## Verification
```bash
python -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab -p 'test_*.py' -v
cmake -S 03-financial-risk/07-financial-and-construction-risk-lab/cpp -B build/construction-risk
cmake --build build/construction-risk
ctest --test-dir build/construction-risk --output-on-failure
```

## Next gates
Dataset contracts; as-of leakage controls; scenario factor correlations; parameter uncertainty; convergence diagnostics; out-of-time backtests; model risk inventory; governance and limits.
