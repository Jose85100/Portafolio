# MVP — scope and maturity

- **What:** reproducible binary-vote simulator and provenance-aware consensus auditor.
- **Run:** `bash reproduce.sh` in this directory (standard library, Python >=3.11).
- **Outputs:** 20 automated tests, 480 experiments, 48 latency/allocation measurements, CSV/JSON/SVG and a notebook with actual in-process outputs.
- **Baselines:** majority, calibrated log-odds weighting; wrong-metadata negative control. Exact 80% acceptance for selective risk.
- **Maturity:** scoped **M2**, parent S1. **Not operational**.
- **Does NOT cover:** real LLMs, multi-class answers, independent truth in production, calibrated confidence, fairness, data privacy controls, authenticated provider provenance, network, authorization, distributed coordination, deployment, or independent validation.
