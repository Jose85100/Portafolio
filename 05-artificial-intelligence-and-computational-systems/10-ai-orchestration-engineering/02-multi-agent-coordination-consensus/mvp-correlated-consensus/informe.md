# Critical report — Correlated-Agent Consensus

**2026-10-22; scoped M2 prototype, parent S1; not operational.** No new scientific voting algorithm is claimed.

## Question and prior art

Does provenance-aware group capping improve selective error when three of five agents share a latent failure mode, and does it fail under independent errors? Related prior art: Dawid–Skene (1979, DOI 10.2307/2346806), Guo et al. (ICML 2017), Geifman–El-Yaniv (2017), Wang et al. (2022), Du et al. (2023) and Ray (OSDI 2018). The methods here are not direct implementations of those papers; see referencias.bib.

## Fixed experiment

Three agents share a common Bernoulli failure event (p=0.20/0.07/0.00); absent a shock, each is correct with probability 0.92. Two independent agents are correct with probability 0.82. Four policies: majority, per-agent log-odds weighted, group-capped, wrong-metadata ablation. Group membership is assumed trusted and known before labels. Weights use Laplace-smoothed calibration from **800 separate cases**; test has **600** cases. **40 paired seeds** (20261022..20261061), three regimes, four policies: **480 evaluations**. Risk@80 accepts exactly 480 highest-margin predictions per test batch; margin is not calibrated correctness probability. Test labels are never used to fit weights or choose accepted cases. AURC is average prefix error.

## Results: 40-seed means, synthetic data only

| Regime | Policy | Accuracy | Risk@80 | AURC |
|---|---|---:|---:|---:|
| Shared failure | Majority | .79229 | .09792 | .06013 |
| Shared failure | Weighted | .85004 | .08323 | .04543 |
| Shared failure | Group capped | **.90738** | **.07547** | **.03938** |
| Shared failure | Wrong metadata | .85004 | .08323 | .04543 |
| Mild dependence | Majority | .91879 | **.02464** | **.01712** |
| Mild dependence | Weighted | .91879 | .02786 | .02018 |
| Mild dependence | Group capped | **.94183** | .04047 | .01786 |
| Mild dependence | Wrong metadata | .91879 | .02786 | .02018 |
| Independent | Majority | **.98658** | .00057 | .00095 |
| Independent | Weighted | **.98658** | **.00036** | **.00056** |
| Independent | Group capped | .96113 | .02417 | .00892 |
| Independent | Wrong metadata | **.98658** | **.00036** | **.00056** |

Paired risk@80 (group minus weighted), bootstrap 95% percentile CI across 40 seeds, 2,000 resamples: shared **−.0077604** [−.0107813,−.0048958]; mild **+.0126042** [.0098958,.0152604]; independent **+.0238021** [.0217187,.0258854]. Conditional on synthetic generator, not independent empirical validation.

## Negative findings and ablations

- Mild dependence: group capping raises overall accuracy but **worsens selective risk**, showing poor confidence ranking.
- Independence: group capping **harms accuracy by 2.55 percentage points** and selective risk by **2.38 percentage points** relative to weighted voting.
- Incorrect provider metadata makes the group-capped rule collapse to weighted voting, removing its improvement.
- Agreement can be jointly wrong; majority is not evidence of truth.

## Reproduction and limitations

`bash reproduce.sh` passed **16 core + 4 artifact tests**. The 32 possible five-agent binary vote patterns are exhaustively checked. Locally `coverage run --branch --source=src -m unittest discover -s tests` covered **88/88 statements and 36/36 branches** in `src/consensus.py` (not whole-repository coverage). 480 raw rows and 48 timing/allocations are generated as CSV, summary JSON, SVG figure and notebook with **four code cells executed in-process**, not through a Jupyter kernel. Python 3.13.5, Linux x86-64, five visible CPUs. Timings exclude model inference and network; tracemalloc is not RSS. Ruff, mypy, Hypothesis, Docker build, CI and C++ sanitizers were not run locally (C++ not used).

**Safety and governance:** synthetic binary tasks, no real LLMs, no PII, no authenticated provenance, no fairness or calibration guarantee, no drift evaluation, no prompt-injection defense, no independent truth, no distributed execution, no production controls. Correlated model errors, poisoned labels and forged provider metadata remain serious risks. **M2 is not a deployable AI system.**
