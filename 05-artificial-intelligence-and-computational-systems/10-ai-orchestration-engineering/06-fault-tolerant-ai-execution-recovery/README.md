# Fault-Tolerant AI Execution & Recovery Engine

**Estado:** S1 — diseño verificable, no motor implementado.

## 1. Mandato, decisión y pregunta

Implementar máquinas de estado durables, checkpoints, retries, backoff, compensaciones y replay.

**Pregunta falsable:** ¿el diseño propuesto mejora recovery time, duplicate side effects, workflow completion, data integrity frente a un baseline simple y reproducible sin introducir fallos de seguridad, integridad o costo?

## 2. Modelo matemático

P(siguiente éxito)=1−(1−p)^n solo bajo intentos independientes; expected cost de reintentos y compensaciones.

Definir formalmente estados, eventos, transiciones, decisiones, restricciones, dominio, horizonte y unidades. Demostrar invariantes, condiciones de terminación y límites de validez. No asumir independencia ni atomicidad de servicios distribuidos sin justificación.

## 3. Modelado estadístico

Fault injection, supervivencia de workflows, distribución de recuperación, pruebas de dependencia. Estimar incertidumbre, dependencia, percentiles de cola y estabilidad entre cargas; registrar tamaños muestrales, seeds, hardware y entorno.

## 4. Arquitectura de implementación

Python durable executor; SQL transaction log; C++ deterministic replay opcional.

**Diseño de carpetas futuro:** `contracts/`, `cpp/`, `python/`, `sql/`, `tests/`, `experiments/`, `security/`, `docs/`. Versionar contratos de eventos y decisiones; separar plano de control y plano de ejecución.

## 5. Pruebas y aceptación

**Métricas:** recovery time, duplicate side effects, workflow completion, data integrity.

- Baseline determinista y escenarios sintéticos con resultado esperado.
- Unit tests, contract tests, integration tests, property tests y fault injection.
- Evaluación de carga, límites de concurrencia, saturación y errores de red.
- Idempotencia de efectos externos, autenticación, autorización y secretos fuera de logs.
- Reproducción de incidentes, rollback y trazabilidad de entradas, salidas y versiones.
- Benchmark con IC y comparación por carga, no una única corrida.

## 6. Entregables y gates

D1 arquitectura y amenaza; D2 contratos y modelo formal; D3 implementación; D4 pruebas y benchmarks; D5 validación independiente; D6 operación y runbook. G0 diseño → G1 modelo → G2 tests → G3 stress → G4 revisión → G5 operación. **D3–D6 pendientes**.

[Fundamentos compartidos](../fundamentals/README.md).
