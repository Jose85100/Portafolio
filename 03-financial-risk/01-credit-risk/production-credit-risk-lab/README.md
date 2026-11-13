# Production Credit Risk Lab — núcleo de validación cuantitativa (M2 parcial)

**Estado:** implementación acotada de métricas y ECL sintética. No es un sistema en producción, modelo calibrado, ni implementación IFRS 9 aprobada. El nombre identifica la arquitectura objetivo, no la madurez alcanzada.

Este laboratorio complementa, sin duplicar, los ejemplos existentes en `../credit-risk-products/`, la investigación de IFRS 9 en `../../04-advanced-research/04-ifrs9-forward-looking-ecl/` y la plataforma de datos en `../../../05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform/`.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 03-financial-risk/01-credit-risk/production-credit-risk-lab/tests -v
```

Sin dependencias externas. `src/validation.py` implementa AUC/Gini con empates, KS con agrupación de scores repetidos, Brier, PSI con bins fijos y suavizado, ECL por hazards condicionales y promedio ponderado de escenarios. `tests/` verifica condiciones límite, invariantes y cálculos manuales.

## Fórmulas implementadas

- `Gini = 2·AUC - 1`. AUC utiliza rangos medios en observaciones empatadas.
- `KS = max_t |F_default(t) - F_nondefault(t)|` sobre umbrales observados y sin romper empates.
- `Brier = (1/n) Σ (y_i - PD_i)^2` para verificar desempeño probabilístico.
- `PSI = Σ (q_j - p_j) ln(q_j / p_j)`, bins anclados en referencia; smoothing pseudoconteos para evitar logaritmos indefinidos.
- `ECL_s = Σ_t S_{t-1,s} h_{t,s} LGD_{t,s} EAD_{t,s} DF_{t,s}`, `S_{t-1} = Π_{k<t}(1-h_k)`, `ECL = Σ_s w_s ECL_s`.

**Límites críticos:** KS/Gini no evalúan calibración. PSI no tiene umbrales universales de aprobación. Hazard condicional no es PD acumulada. Stage 3 debe modelarse separadamente mediante déficits de flujos y recuperaciones descontadas; la tasa de descuento debe responder a la metodología EIR aplicable. La decisión SICR necesita política aprobada y criterios cuantitativos/cualitativos. No utilizar estos cálculos directamente para contabilizar provisiones.

## Roadmap e integración

1. **Scorecard y PD:** WoE sin fuga de objetivo; regularización, monotonía justificada, calibración Platt/isotónica, intervalos bootstrap por cliente y OOT por vintage. Comparar logística vs gradient boosting vs hazard discreto.
2. **IFRS 9:** contractual vs conductual, prepagos, PD marginal, LGD de recuperación, EAD y CCF, SICR, 12 meses vs lifetime, escenarios de política macro, descuentos, tratamiento diferenciado de activos en incumplimiento.
3. **Validación independiente:** discriminación, fiabilidad de PD, backtesting por cohorte, intervalos, fairness, drift y pruebas de sensibilidad contra umbrales versionados.
4. **MLOps:** contratos de features point-in-time, registry versionado, metadatos de entrenamiento, aprobación de segundo revisor, inferencia batch y API, observabilidad, rollback probado, idempotencia y auditoría de cambios.
5. **Data engineering:** PostgreSQL para extracción reproducible; Spark / Parquet para datos de escala; reconciliación de fuentes, cortes temporales, aislamiento y manejo de PII bajo política.
6. **Cloud AWS de referencia:** S3 cifrado, IAM mínimo privilegio, jobs de entrenamiento, registry, procesamiento batch y endpoint con monitoreo. Diseño, no infraestructura desplegada.

### Criterios de promoción a producción

Se exige evidencia externa de calidad de datos, muestras representativas, definición y gobierno de default, validación temporal e independiente, calibración y backtesting, controles de seguridad y privacidad, métricas de operación, recuperación ante fallos, aprobación contable y modelo de segregación de funciones. Un test sobre datos sintéticos no satisface ninguno por sí solo.

## Documentos

- [Runbook y matriz de gobierno](docs/PRODUCTION_CONTROLS.md)
- [Consultas SQL point-in-time y backtesting](sql/credit_validation.sql)

**Licencia y datos:** solo código y pruebas sintéticas. Sin datos de clientes.
