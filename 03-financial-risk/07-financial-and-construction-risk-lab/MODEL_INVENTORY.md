# Model inventory and maturity

| Track | Projects | Maturity |
|---|---:|---|
| Corporate financial risk | 7 | 7 specifications |
| Construction enterprise risk | 15 | 1 Monte Carlo prototype, 14 specifications |
| Research in progress | 10 | 10 specifications |
| **Total** | **32** | **1 prototype, 31 specifications** |

The first prototype uses synthetic assumptions, with no empirical calibration, CI verification or independent model validation claimed.

## Priority build order
1. Integrated project cash flow, cash shortfall, DSCR and NPV-at-Risk.
2. CPM/PERT delays + materials cost shocks + presales and cancellation models.
3. Portfolio aggregation, concentration and joint macro stress.
4. Counterparty and contractor networks, climate and permit risks.
5. Causal, Bayesian, robust optimization and real options research.

## Release gates
- **S0**: documented research hypothesis and data contract.
- **S1**: tested algorithmic baseline with synthetic fixtures.
- **S2**: data quality checks, calibrated estimates, reproducible evaluation.
- **S3**: independent validation, stress, monitoring and model governance.
- **S4**: controlled operational deployment with overrides and audit logs.

**Never infer production readiness from a README or passing unit tests alone.**
