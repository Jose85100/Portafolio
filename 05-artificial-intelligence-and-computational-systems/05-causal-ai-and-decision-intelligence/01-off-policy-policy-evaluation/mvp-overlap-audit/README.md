# Off-policy evaluation: positivity, cross-fitting and mislogged propensities

**CICLO_DIARIO — 2026-10-15.** Incremental MVP for the existing S1 project
`05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation`.
**Maturity: M2, locally verified synthetic prototype, NOT operational.**

## One command

From this project directory (Python >=3.10, standard library only, no API keys/network):

```bash
bash reproduce.sh
```

This runs 15 unittest methods (including 100 deterministic generative examples),
120 paired synthetic datasets × 6 estimators = **720** raw rows, an SVG chart,
summary JSON, timing CSV, and four genuinely executed notebook cells with visible outputs.
A CI workflow runs the same command on Python 3.12. No pip installation required.

Optional coverage (when `coverage` is installed):

```bash
python3 -m coverage run --source=src -m unittest discover -s tests -q
python3 -m coverage report -m
```

## Scientific question and hypothesis

Can three-fold cross-fitted doubly robust (DR) off-policy evaluation reduce
RMSE relative to inverse propensity scoring (IPS), particularly under weak
positivity or misreported logging propensities? The falsifiable primary metric
is per-seed squared-error difference (IPS minus DR), assessed using a paired
bootstrap across 40 independent seeds. A negative 95% interval would refute
improvement in that regime. We also compare SNIPS, direct method (DM), and
clipped IPS/DR (clip=8) as negative controls.

**Prior art:** IPS/SNIPS, doubly robust OPE, cross-fitting and clipping are
established methods (see `referencias.bib`), not inventions of this MVP.
The incremental contribution is a tiny auditable implementation, synthetic
oracle, propensity-mislogging ablation, ESS diagnostic, and executable tests.

## Data generating process

- Binary context X ~ Bernoulli(0.5), two actions and binary reward.
- Reward means `P(R=1|X,A)`: `[[.15,.55],[.70,.30]]`.
- Target policy: A=1-X, exact population value **0.625**.
- Logging policy selects target action with probability 0.50 (well overlap),
  0.04 (weak overlap), or 0.04 but **reports** 0.20 (misspecification).
- 40 independent seeds starting at 20261015, n=600 per seed.
- Three-fold out-of-fold categorical reward model with Beta(1,1) smoothing.
- No covariate shift, unobserved confounding, delayed feedback, or interference.
- `ESS < 30` triggers a `LOW_ESS` warning; estimates remain in the audit
  dataset but **must not be treated as approved deployment estimates**.

## Structure

- `src/ope.py`: deterministic simulator, exact oracle, cross-fit, six estimators, diagnostics.
- `tests/test_ope.py`: numerical/edge/generative tests, self-leakage guard.
- `benchmarks/run.py`: paired Monte Carlo, 2,000-resample seed bootstrap,
  time/tracemalloc, raw CSV, summary JSON, SVG figure.
- `tools/build_notebook.py`: executes four narrative cells in-process and captures
  their real outputs without opening a Jupyter kernel socket.
- `results/`: retained raw and aggregate results (machine-dependent timings).
- `informe.md`: assumptions, results, negative ablations, threats to validity.
- `MVP.md`: precise maturity and scope. `Dockerfile`: optional environment recipe.

## Limitations and warnings

`LOW_ESS` is a diagnostic threshold, **not a confidence guarantee**. DR is not
universally superior; the reward model is low-dimensional and well specified.
Incorrect propensities invalidate IPS identification and do not generally
preserve DR consistency unless the reward model is correct. Do not use this
prototype for credit decisions, risk limits, health decisions or real users.
See `informe.md` for security/privacy/governance and negative results.
