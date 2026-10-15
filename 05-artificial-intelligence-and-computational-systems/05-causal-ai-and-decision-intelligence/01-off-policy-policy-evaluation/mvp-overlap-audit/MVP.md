# MVP contract and maturity

- **What:** an offline evaluator of a deterministic two-action contextual bandit,
  with IPS, SNIPS, DM, cross-fitted DR, clipped IPS and clipped DR.
- **Where:** `05-artificial-intelligence-and-computational-systems/05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation/mvp-overlap-audit/`.
- **How:** `bash reproduce.sh` (Python >=3.10, stdlib only).
- **Outputs:** 720-row raw CSV, 120 timing observations, summary JSON,
  SVG RMSE chart, executed notebook and 15 passing tests.
- **Baseline:** literature-established IPS and SNIPS, as the S1 repository project
  had no runnable baseline; no artificial claim of an existing repo baseline.
- **Maturity:** **M2 — verified local prototype** for this isolated component;
  parent project's other design ambitions remain S1.
- **NOT covered:** real logs, point-in-time event ingestion, learned target
  policies, external datasets, general multi-action OPE, nonstationarity,
  correct inference under nuisance misspecification, unknown behavior policy,
  unobserved confounding, independent validation, operational controls or deployment.
- **Integrity:** original S1 specification is preserved, and data-engineering
  contracts/shared code remain untouched.
