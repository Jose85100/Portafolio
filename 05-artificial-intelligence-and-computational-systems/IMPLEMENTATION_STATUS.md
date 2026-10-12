# Implementation status

## Fourteen standalone computational prototypes

Each of the 14 projects in pillars 02–08 now has a dependency-free Python `src/model.py` and a `tests/test_model.py` with a deterministic smoke/invariant test. Run:

```bash
python 05-artificial-intelligence-and-computational-systems/scripts/test_projects.py
```

CI runs the same suite on Python 3.11–3.13. Existing Data Engineering code and its two workflows are retained.

### Scientific maturity

These are **working algorithmic baselines, not complete research systems or production services**. For example, the temporal-model project implements leakage-safe evaluation, not a trained foundation model; the agent research project verifies citations, not an LLM orchestration platform; GraphRAG implements temporal retrieval, not a full graph database. Results on real data, statistical calibration, scale benchmarks, security reviews and external validation remain pending. Tests verify essential behavior, not full correctness or statistical validity.

### Next milestones

1. Establish versioned public datasets, data contracts, provenance and as-of availability checks.
2. Add property-based tests, adversarial fixtures, statistical simulation and performance budgets.
3. Introduce optional production integrations behind adapters and pinned dependency locks.
4. Implement full model families (Bayesian change points, transformers, agent orchestration, causal DR estimators, graph retrieval) without overstating current scope.
