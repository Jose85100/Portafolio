# Correlated-Agent Consensus — M2 synthetic audit

**Project:** 10-ai-orchestration-engineering/02-multi-agent-coordination-consensus/mvp-correlated-consensus. The parent project is S1; this component is an M2 verified local prototype, **not operational**.

## One-command reproduction

From the repository root:

```bash
bash 05-artificial-intelligence-and-computational-systems/10-ai-orchestration-engineering/02-multi-agent-coordination-consensus/mvp-correlated-consensus/reproduce.sh
```

Python >=3.11 standard library only. No internet, API keys, external models or GPUs. Runs 16 core tests, 480 seeded policy evaluations, 48 latency/allocation samples, four code cells executed **in-process** (not a Jupyter kernel), and four artifact tests. Generates `results/raw.csv`, `results/summary.json`, `results/latency.csv`, `results/risk.svg` and `notebook.ipynb`. Raw artifacts are also included in the downloadable local ZIP.

Optional local coverage:
```bash
python3 -m coverage run --branch --source=src -m unittest discover -s tests
python3 -m coverage report -m
```
Measured locally: **100% of 88 statements and 36 branches in src/consensus.py**. Not whole-repository coverage. Ruff, mypy, Hypothesis, Docker build and remote CI were not executed; C++ sanitizers are not applicable.

## Hypothesis and design

Do correlated provider failures undermine five-agent majority? Does discounting the three votes from one shared provider improve selective risk at **matched 80% coverage** and harm it under independent errors?

All policies share the same held-out cases. Reliability weights are learned only from separate calibration labels; provider IDs are assumed known. Policies: majority, log-odds weighted, provider-group-capped, and wrong-metadata ablation. A group contributes one normalized vote. This is a heuristic, not a novel optimal aggregation rule. Confidence is a normalized margin, not a calibrated probability.

Generator: three agents share a Bernoulli failure shock at p=.20/.07/0; absent the shock, each is correct with p=.92. Two other agents are independently correct with p=.82. 40 seeds, 800 calibration and 600 test cases per seed/regime. Results are conditional on this generator; see `informe.md` for paired bootstrap intervals, negative controls, privacy, governance and limitations.
