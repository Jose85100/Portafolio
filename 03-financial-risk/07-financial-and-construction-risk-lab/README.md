# Financial & Construction Risk Lab

**32 quantitative risk projects** across corporate financial risk (7), construction enterprise risk (15), and advanced research (10). See [model inventory](MODEL_INVENTORY.md) for implementation maturity and release gates.

## Core decision problem
Quantify project solvency, cash shortfall, schedule/cost risk, presales, financing covenants and portfolio-level tail loss under common macro shocks. Outputs include P(min cash < floor), peak cash-shortfall quantiles, DSCR breach, NPV-at-Risk, VaR/CVaR and reverse stress.

## Code status
Only `02-construction-enterprise-risk/01-project-cashflow-at-risk/src/model.py` currently contains a reproducible Monte Carlo baseline; the other 31 folders are research specifications, **not implemented models**. Inputs are synthetic; no real-world calibration or independent validation.

## Run baseline unit tests
```bash
python -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/01-project-cashflow-at-risk/tests -p 'test_*.py' -v
```

## Model development protocol
Point-in-time data contracts, leakage prevention, estimation uncertainty, dependence and tail risk, rolling backtests, independent validation, documented use limits and model risk governance.
