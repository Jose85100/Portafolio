# Critical report: global conformance versus local transitions

**Date:** 2026-10-16. **Hypothesis:** A global path check has higher anomaly recall than a pairwise direct-follows baseline for hybrid traces. **Question:** Can individually allowed edges form a globally forbidden trace? Yes.

**Prior art:** van der Aalst (2016), Process Mining Manifesto (2012), Adriansyah et al. (2011, 2014), van der Aalst and Verbeek (2014), Berti et al. (2019). The incremental contribution is a transparent reproducible finite-language demonstration, not a new Petri-net aligner. Search is targeted, not exhaustive.

**Experimental configuration:** four explicit approved paths; 30 seeds (20261016–20261045), three regimes with 48, 30 or 12 hybrid anomalies among 60 anomalies, plus 60 clean cases each. 90 datasets × 120 cases = 10,800 synthetic cases, four paired detectors = 360 evaluations. Labels use `trace in PATHS`, independent of the aligner implementation but defined against the same reference paths. No training or model selection.

**Measured mean anomaly recall:** hybrid-heavy: activities 0.055, pairs 0.200, tolerant alignment 0.048, strict alignment 1.000. Balanced: 0.131/0.500/0.118/1.000. Local-heavy: 0.203/0.800/0.195/1.000. Pairs miss 1440/900/360 anomalies over 30 seeds per regime. Strict alignment has F1=1 by construction. The tolerant alignment ablation is negative, missing most single-edit anomalies; activity-only is worse. The null of equal recall is refuted **within this synthetic design**, not on real logs.

**Performance:** dynamic programming O(Knm) time, O(nm) space for K approved paths; slower than pairwise. `results/per_seed.csv` records per-batch time and peak Python allocations measured with `tracemalloc`, not RSS. No claim of real-time performance or production scalability. Python version, platform, machine, seeds recorded in `results/config.json`.

**Risks and failure modes:** Four-path oracle makes perfect recall tautological. If the authorized model is incomplete or obsolete, false positives follow. Partial/in-flight cases, duplicate events, ambiguous timestamps, distributed concurrency, process drift, missing event data, privacy, access control and independent expert labels are untested. No causal inference from waits, no operational system. Docker build, mypy, Ruff, Hypothesis, or independent CI are not claimed as executed locally.

**Next:** evaluate licensed real event logs and PM4Py baseline; model version changes and temporal holdouts; add event-contract, privacy and security controls.
