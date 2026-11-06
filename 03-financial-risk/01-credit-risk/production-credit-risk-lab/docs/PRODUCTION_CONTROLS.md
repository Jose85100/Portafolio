# Controles para habilitación de modelos crediticios

| Puerta | Evidencia exigida | Owner | Bloqueo |
|---|---|---|---|
| Contrato de datos | corte temporal, observación, definición default, latencias, hashes, trazabilidad | Data Engineering | leakage / duplicidad / cambios de esquema |
| Model development | especificación, variables, splits temporales, hiperparámetros, calibración, reproducibilidad | Model Development | sobreajuste / target leakage |
| Validación independiente | KS/Gini, calibración, Brier, backtesting por vintage, intervalos y challenge | Model Validation | fallo de validación o población inadecuada |
| Gobierno IFRS 9 | SICR, escenarios, consistencia marginal/lifetime, LGD/EAD, EIR, overlays, conciliación contable | Riesgo + Finanzas | provisión sin aprobación |
| Privacidad y seguridad | protección de PII, RBAC, cifrado, auditoría, retención, revisión legal | Seguridad / Legal | incumplimiento |
| Deploy | versionado inmutable, dual approval, pruebas canary y rollback, SLA/SLO | MLOps + Riesgo | sin recuperación demostrada |
| Monitoreo | datos, PD observada, calibración, morosidad, estabilidad, incidentes | MRM + Operaciones | drift severo sin respuesta |

**Cadencia objetivo:** vigilancia técnica diaria/semanal, performance mensual o trimestral condicionado al período de maduración de default, revisión anual o gatillada por cambio significativo. Los umbrales deben calibrarse frente a los costos de falsos positivos e incertidumbre; no usar PSI 0.1/0.25 como aprobación automática.

## Diseño de registro de modelo

Manifest mínimo: `model_id`, `version`, `git_sha`, `training_data_hash`, `training_cutoff`, `target_definition_version`, `feature_contract_hash`, `calibration_version`, `validation_report_sha`, `approved_by`, `approved_at`, `deployment_environment`, `rollback_version`.

Para cada inferencia: request ID seudonimizado, versión, fecha de corte de features, fecha efectiva, código de resultado, tiempo de respuesta y motivo de abstención. No almacenar datos sensibles en logs planos.

## Restricciones y valor de investigación

El stack es **Python + SQL de referencia**, extendible a PySpark. Ninguna ruta de AWS, Docker, MLflow o Airflow ha sido desplegada aquí; no declarar disponibilidad ni throughput. Para validación científica: comparación OOT por cohorte, bootstrap por cluster y experimentos de stress no estacionario, con resultados negativos publicados.
