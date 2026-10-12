# Enterprise Risk Advisory — arquitectura de referencia

## Modelo de dominio

Ocho prácticas, siete proyectos por práctica. Compartir definiciones de **exposición, evento, pérdida, escenario, horizonte, unidad monetaria, corte, fuente, control, modelo, versión, resultado y decisión**, sin forzar una distribución o función de pérdida única.

## Capas

1. Fuentes y permisos: registros autorizados, normativa y datos públicos.
2. Contratos y calidad: grano, as-of date, fecha de disponibilidad, unidades, lineage, reconciliación.
3. Motores de dominio: C++17/20 para kernels numéricos; Python para estimación, validación y orquestación; SQL para preparación point-in-time.
4. Escenarios y agregación: escenarios comunes, dependencia entre pérdidas monetizables, límites de capital y liquidez; indicadores no monetarios separados.
5. Gobierno y decisión: validación independiente, registro de modelos, KRIs, límites, comité y evidencias.

## Interfaz mínima versionada (propuesta)

```text
RunContext/v1: run_id, model_id, model_version, as_of, scenario_id, seed, units
RiskInput/v1: entity_id_pseudonymous, risk_type, exposure, horizon, observation_time, available_time
RiskEstimate/v1: measure, value, unit, horizon, uncertainty, assumptions, diagnostics
ValidationReport/v1: baseline, tests, error, drift, sensitivity, independent_review
DecisionRecord/v1: owner, action, threshold, approval, evidence_ref, timestamp
```

No persistir datos personales ni credenciales en Git. Alinear cálculos y gobernanza a requisitos específicos por jurisdicción; no afirmar cumplimiento automático de SFC, Basel, IFRS, SBS, ISO o NIST.

## Reglas matemáticas

- La pérdida agregada L=Σ_k L_k requiere dependencia conjunta; no sumar VaR o ES individuales como si fueran capital diversificado.
- EL=Σ_i E[D_i LGD_i EAD_i]. Factorizar en PD×LGD×EAD solo bajo condiciones suficientes y horizontes consistentes.
- ESα(L)=(1/(1−α))∫_α^1 VaR_u(L)du es válida también para distribuciones con átomos (cuantil generalizado).
- Para procesos de duración, tratar censura, truncamiento y selección.
- Para inferencia causal, explicitar identificación y sensibilidad a confusión.
- Para riesgos no monetarios, usar métricas de control y resiliencia en lugar de pérdidas inventadas.

## Ciclo de entrega y puertas de control

S1 especificación falsable; S2 prototipo ejecutable con tests; S3 validación temporal, numérica y estadística; S4 revisión independiente y datos públicos o autorizados; S5 gobierno, documentación y despliegue controlado. No promover sin evidencia.

## Estructura de código por proyecto (objetivo)

```text
cpp/include/     # contratos y kernels de alto rendimiento
cpp/tests/       # pruebas numéricas, invariantes y sanitizers
python/src/      # calibración, simulación y análisis
python/tests/    # pruebas estadísticas y equivalencia con C++
sql/             # tablas, vistas point-in-time y controles
experiments/     # seeds, escenarios, benchmarks, artefactos
reports/         # metodología, validación y decisiones
```

La presente PR añade especificaciones; **no añade 32 motores ejecutables**.
