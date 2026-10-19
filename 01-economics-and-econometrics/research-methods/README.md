# Research methods — identification, reproducibility and falsification

## Scope
This module provides an **educational, tested point-estimation kernel**, not an econometrics package. The bivariate routines include an intercept and deliberately do not accept controls. No standard errors or weak-instrument robust confidence sets are implemented. Never present the synthetic estimates as evidence from a real economy.

## Structural DGP and probability limits
Assume mutually independent unit-variance `z,u,v`, with `x=pi*z+delta*u+v` and `y=beta*x+u`. The true causal coefficient is `beta`. Since `Cov(x,u)=delta` and `Var(x)=pi²+delta²+1`,
```math
\operatorname{plim}\hat\beta_{OLS}=\beta+\frac{\delta}{\pi^2+\delta^2+1}.
```
For `pi != 0`, exclusion and independence imply `Cov(z,u)=0` and `Cov(z,x)=pi`; therefore `plim beta_IV=Cov(z,y)/Cov(z,x)=beta`. If `pi=0`, the population ratio is undefined; for small `pi`, finite-sample IV can be unstable even when the denominator is not exactly zero. The implemented numerical threshold is **not** a weak-instrument diagnostic.

## Reproduce from repository root
```bash
python -m unittest discover -s 01-economics-and-econometrics/research-methods/tests -p 'test_*.py' -v
python 01-economics-and-econometrics/research-methods/benchmarks/identification_study.py
```
The benchmark runs 60 Monte Carlo replications at each of four instrument strengths with n=600; it reports OLS/IV bias and RMSE. The purpose is to demonstrate the identification–precision tradeoff, not to claim a fixed performance threshold across all DGPs.

## Review gate for every research project
1. Define economic question, population, treatment/shock, outcome, estimand and units.
2. State behavioral/equilibrium model and mathematical assumptions; derive comparative statics or moment conditions.
3. State identification assumptions, threats, and observational equivalence.
4. Implement DGP, independent numerical oracle, negative controls and seed policy.
5. Report finite-sample bias, RMSE, interval coverage, numerical tolerance and runtime.
6. Add genuine data provenance, vintage/time-split strategy, transformations and missingness handling.
7. Document counterfactual policy implications and welfare/risk distribution, with uncertainty.
8. Include reproducibility commands, expected artifacts, references, known failure modes and model status.

## Limitations
No controls, heteroskedasticity-robust inference, clustering, panel methods, LATE heterogeneity, sample selection correction, HAC or real data. Those require explicit extensions and independent validation.
