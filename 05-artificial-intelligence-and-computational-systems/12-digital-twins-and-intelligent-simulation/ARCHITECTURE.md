# Digital Twin Platform — arquitectura de referencia

```text
Sources / Sensors / Public Data
  -> Ingestion + Point-in-Time Validation
  -> Observation Store + Event Log
  -> State Estimator / Data Assimilation
  -> Calibrated Dynamic Simulator
  -> Scenario + Counterfactual Engine
  -> Policy Evaluation + Optimization
  -> Validation + Model Registry + Decision Evidence
```

## Contratos propuestos

`TwinObservation/v1`: entity_id, event_time, available_time, variable, value, unit, source, quality.

`TwinState/v1`: twin_id, as_of, state_vector, posterior_uncertainty, model_version.

`TwinScenario/v1`: scenario_id, horizon, exogenous_paths, intervention, assumptions, seed.

`TwinRun/v1`: run_id, state_ref, scenario_ref, code_version, seed, numerical_tolerances, outputs.

`TwinValidation/v1`: backtest window, state estimation error, interval coverage, stress, stability, independent reviewer.

## Criterios mínimos

1. Actualización de estado con observaciones temporalmente disponibles.
2. Comparación con baseline estático y modelo temporal sencillo.
3. Pruebas de convergencia numérica y consistencia de unidades.
4. Incertidumbre propagada a escenarios y decisiones.
5. Separación entre simulación, inferencia causal y política óptima.
6. Gobernanza, seguridad, límites de uso y reproducibilidad.

**Estado:** especificación S1; no hay motor de gemelos implementado en esta carpeta.
