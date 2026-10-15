# Technical report — CICLO_DIARIO 2026-10-15

## 1. Scope
The existing Off-Policy Decision Evaluation project was design-only S1. This
isolated M2 executable numerical audit implements established estimators rather
than proposing a novel algorithm.

## 2. Identification and experimental design
Let X,A,R be binary. Target action is 1-X. With consistency, positivity and
conditional exchangeability, the target value is identifiable. The simulator
supplies these assumptions by construction; the reward matrix is
[[0.15,0.55],[0.70,0.30]], so V=0.625 exactly.

For w_i=1[A_i=1-X_i]/p_i, IPS=mean(wR), SNIPS=sum(wR)/sum(w), and
DR=mean(mhat_i+w_i(R_i-mhat_i)). DM=mean(mhat_i). Clipped estimators replace
w_i by min(w_i,8). Three-fold cross-fitting prevents training on the same row.
All six estimators see identical observations within each regime and seed.

Three regimes: true/reported p=.50/.50, .04/.04, and .04/.20. 40 seeds,
600 observations per seed, 2,000 paired bootstrap draws, and an ESS<30 warning.
Bootstrap intervals cover the mean paired MSE difference across seeds,
not an individual policy-value confidence interval.

## 3. Results executed locally
Python 3.13.5, Linux x86-64, AMD EPYC 9V74. 120 paired datasets and 720 rows.

| Regime | IPS RMSE | SNIPS | DM | DR | clipped IPS | clipped DR | low ESS |
|---|---:|---:|---:|---:|---:|---:|---:|
| p=.50/.50 | .0409 | .0285 | .0292 | .0295 | .0409 | .0295 | 0% |
| p=.04/.04 | .1366 | .0917 | .0742 | .0895 | .4351 | .0772 | 90% |
| p=.04/.20 | .5057 | .0917 | .0742 | .0759 | .5057 | .0759 | 90% |

Paired 95% percentile intervals for IPS minus DR MSE:
[-0.0001055,0.0018772], [0.0021559,0.0219856],
[0.2408033,0.2582432] respectively.
Local wall time 0.983 seconds, peak Python tracemalloc 497205 bytes.
Machine-dependent timings are not portable CPU/RSS benchmarks.

## 4. Negative ablations
- At high overlap, the paired interval includes zero: no strong DR superiority.
- Under weak overlap, DM (.0742) beats DR (.0895) on RMSE.
- IPS clipping at 8 introduces large bias when the correct weight is 25.
- Mislogged propensity destroys IPS accuracy; SNIPS cancels this specific
  constant propensity scaling, not arbitrary misspecification.
- ESS<30 flags 90% of low-overlap runs; flagged estimates are not approved.
- True zero support is rejected; no observed target action makes SNIPS undefined.

## 5. Tests and limitations
15 unittest methods including 100 seeded generative cases passed locally.
Statement coverage for src/ope.py was 120/120=100% (not branch or
project-wide coverage). Four notebook cells executed in-process.
Ruff, mypy, Hypothesis and Docker build were not executed; they are not
installed or were not attempted. This is not independent validation.
No PII or external customer data were used.

Unknown behavior propensities, confounding, action-dependent missingness,
groupwise overlap, delayed rewards, distribution shift and selective labels
can invalidate identification. Real deployments require immutable propensity
logging, privacy controls, auditability, fairness reviews, independent
validation and human governance. This is an M2 synthetic prototype only.

## 6. Prior art
Seven verified sources appear in referencias.bib: Dudik (2011), Li (2010),
Swaminathan/Joachims (2015), Wang et al. (2017), Bottou et al. (2013),
Thomas/Brunskill (2016), Kallus/Uehara (2020).
