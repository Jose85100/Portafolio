# Prior concentration sensitivity (2026-11-05)

Continuation of `pricing-pilot-evsi-gate`. Three candidates considered: (1) CARA-utility EVSI, needing risk-preference calibration; (2) Beta prior-concentration sensitivity with fixed means, selected because it refutes dependence of the gate on a single subjective prior without changing the existing decision model; (3) explicit delay-cost model, deferred until an operational delay contract exists.

## Hypothesis and formula

For Beta(a,b), preserve mean m=a/(a+b) while multiplying concentration κ=a+b by c>0: a'=cm and b'=c(1-m). Posterior predictive conversion remains Beta-Binomial; exact enumeration in the existing `evaluate` computes EVSI(c). Hypothesis: with this fixed synthetic two-price example and n=20/arm, EVSI is non-increasing over c in {0.25,.5,1,2,4,10,100}; this is a scenario-specific falsifiable claim, not a general theorem.

## Reproduction and evidence

`PYTHONPATH=src python -m unittest discover -s tests -v`; `PYTHONPATH=src python src/run_prior_sensitivity.py`. The latter emits CSV, JSON and PNG. All eleven old+new tests pass. Data are synthetic; economics are abstract contribution units/customer. Five references are in `referencias.bib`; this is sensitivity auditing/adaptation of classical EVSI, not a new formula or empirical pricing recommendation. Limitations: two independent arms, fixed margins, no repeat purchases, delay or capacity effects.

Notebook `notebooks/prior_sensitivity.ipynb` executed in order via `scripts/execute_prior_notebook.py` (IPython in-process): the local sandbox blocks Jupyter kernel network-interface discovery before cell execution. The notebook has visible table and PNG outputs; remote CI kernel execution remains unverified.

### Numerical roundoff at high concentration
Theoretical EVSI is nonnegative because the maximum of conditional expected values is convex. At c=100 the existing floating Beta-Binomial enumeration returns a raw EVSI about -1.85e-10, while predictive mass differs from one by 3.36e-12. We retain the raw value, flag `evsi_negative_roundoff=true`, and enforce a declared diagnostic bound `1e-11 * max(1, |baseline_value|)` (5.5e-10 in this fixture). This is numerical tolerance, not evidence of negative information value or a general accuracy guarantee.
