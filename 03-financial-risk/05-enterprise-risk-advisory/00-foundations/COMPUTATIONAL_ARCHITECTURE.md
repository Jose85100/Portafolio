# Arquitectura computacional y contratos

## 1. Principio

**Separación estricta** entre contratos de dominio, estimación, kernels numéricos, validación, almacenamiento y presentación. Un proyecto no crea un segundo motor de escenarios si puede usar uno versionado.

## 2. Lenguajes y responsabilidades

- **C++20:** Monte Carlo, simuladores de eventos, algoritmos de grafos, optimización y pricing intensivo; librerías de dominio sin conectores ni secretos.
- **Python:** calibración, econometría, inferencia bayesiana, generación de datos sintéticos, comparación de métodos, gráficos y experimentos.
- **SQL:** datos point-in-time, granularidad, joins temporales, conciliación, calidad y linaje.
- **JSON Schema/Parquet:** contratos versionados; elegir formatos por interoperabilidad, no por conveniencia.

## 3. Contratos propuestos

`RunContext/v1`: run_id, model_id, model_version, as_of, horizon, currency, seed, scenario_id, code_hash, input_hash.

`RiskObservation/v1`: entity_pseudonym, risk_type, event_time, available_time, source, unit, value, quality_flags.

`Scenario/v1`: scenario_id, horizon, drivers, shocks, probability_if_applicable, assumptions.

`RiskEstimate/v1`: measure, estimate, unit, horizon, uncertainty, diagnostics, limitations.

`ValidationReport/v1`: tests, baselines, coverage, numerical_error, drift, independent_review, approval.

## 4. Integración

```text
sources → SQL point-in-time → typed contracts → Python calibration
                                      ↓
                             C++ numerical kernels
                                      ↓
                         results + validation evidence
                                      ↓
                         risk committee / decision logs
```

## 5. Pruebas de software

Compilar con `-Wall -Wextra -Werror`, sanitizers cuando proceda, pruebas unitarias y property-based, equivalencia Python–C++, benchmarks con semillas, verificación de unidades y contratos, CI y revisiones independientes. Prohibir credenciales, PII y datos reales no autorizados en Git.

## 6. Regla de madurez

Una carpeta con `README.md` es **diseño**. Solo declarar implementación cuando existan fuentes, pruebas ejecutadas y resultados reproducibles. Ningún motor se considera apto para producción sin validación adicional.
