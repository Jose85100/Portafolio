# MVP contract — 2026-10-16

**What:** Finite-language conformance audit using exact edit-distance alignment, two weak baselines and one negative ablation.

**Run:** `bash 05-artificial-intelligence-and-computational-systems/07-intelligent-automation-and-process-mining/01-process-mining-risk-operations/conformance-mvp/reproduce.sh` from repository root; Python >=3.12.

**Produces:** executable modular Python in `src/`, 11 automated test methods, 360 paired evaluations on 10,800 synthetic cases, raw CSV/JSON, SVG, notebook with executed outputs, runtime and Python-allocation measurements.

**Does not cover:** BPMN/Petri models, loops not enumerated, parallelism, incomplete cases, independent labels, real logs, causal bottlenecks, production authorization/privacy controls, scaling, monitoring, SLOs, Docker build verification.

**Maturity:** S1 specification → scoped M2 locally verifiable component. This does not advance the whole pillar or domain to M2/M3; it is not operational.
