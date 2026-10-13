# Interoperable economic twin contracts — conceptual v1

Schemas must eventually be implemented and validated as JSON Schema/Protobuf. Do not conflate these conceptual examples with a production API.

## EconomicObservation/v1

```json
{"schema_version":"1","series_id":"GDP_REAL","region":"COL","sector":"TOTAL","event_time":"2026-03-31T23:59:59Z","available_time":"2026-05-15T00:00:00Z","vintage":"first_release","frequency":"quarterly","value":100.0,"unit":"index","source":"licensed_public_dataset","quality":"unverified_example"}
```

## EconomicTwinState/v1

```json
{"schema_version":"1","twin_id":"labor-market","as_of":"2026-05-15T00:00:00Z","state_hash":"sha256","geography":"COL","frequency":"quarterly","latent_state_ref":"artifact-uri","uncertainty_ref":"artifact-uri","model_version":"0.1.0"}
```

## EconomicScenario/v1

```json
{"schema_version":"1","scenario_id":"ai-adoption-high","horizon_quarters":20,"baseline_ref":"artifact-uri","interventions":[],"exogenous_paths_ref":"artifact-uri","assumptions_ref":"artifact-uri","seed":42}
```

## CouplingFlow/v1

```json
{"schema_version":"1","producer":"technology-diffusion","consumer":"labor-market","variable":"sector_adoption_rate","region":"COL","sector":"J","frequency":"quarterly","unit":"share","aggregation":"weighted_mean","available_time":"2026-05-15T00:00:00Z","value":0.2,"uncertainty_ref":"artifact-uri"}
```

## SimulationResult/v1

run_id, input hashes, code/model versions, state version, scenario, RNG streams, numerical tolerances, hardware, outputs, confidence/credible intervals, convergence diagnostics, assumptions and warnings.

## ValidationResult/v1

experiment_id, pre-registered hypothesis, baseline, train/test vintage, data license, estimand, identification assumptions, tests, metrics, uncertainty, sensitivity, reviewer and decision status.

## Invariants

- No observation available after a decision timestamp is used in that decision.
- Stock-flow reconciliation holds to declared tolerance and frequency.
- Monetary variables use currency and real/nominal/price-base metadata; rates specify units and compounding.
- Spatial/sector aggregation uses weights and classification concordances, not naive sums of rates.
- Coupled outputs retain uncertainty and provenance; a scenario result is never silently relabeled as causal impact.
- Synthetic data and assumptions are explicitly tagged; no private data in the public repository.
