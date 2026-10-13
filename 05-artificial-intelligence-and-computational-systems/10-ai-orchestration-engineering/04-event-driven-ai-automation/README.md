# Event-Driven AI Automation Platform

**Estado:** S1 — diseño verificable, no motor implementado.

## 1. Mandato, decisión y pregunta

Procesar eventos de negocio y disparar workflows con garantías explícitas de entrega e idempotencia.

**Pregunta falsable:** ¿el diseño propuesto mejora event lag, duplicates prevented, replay correctness, DLQ rate frente a un baseline simple y reproducible sin introducir fallos de seguridad, integridad o costo?

## 2. Modelo matemático

Estado s_{t+1}=δ(s_t,e_t); deduplicación por event_id; balance λ<μ para estabilidad de cola simple.

Definir formalmente estados, eventos, transiciones, decisiones, restricciones, dominio, horizonte y unidades. Demostrar invariantes, condiciones de terminación y límites de validez. No asumir independencia ni atomicidad de servicios distribuidos sin justificación.

## 3. Modelado estadístico

Modelos de llegadas, burstiness, retraso, reordenamiento y pruebas de carga. Estimar incertidumbre, dependencia, percentiles de cola y estabilidad entre cargas; registrar tamaños muestrales, seeds, hardware y entorno.

## 4. Arquitectura de implementación

Python consumers/producers; Kafka/NATS opcional; SQL outbox/inbox; C++ workers opcionales.

**Diseño de carpetas futuro:** `contracts/`, `cpp/`, `python/`, `sql/`, `tests/`, `experiments/`, `security/`, `docs/`. Versionar contratos de eventos y decisiones; separar plano de control y plano de ejecución.

## 5. Pruebas y aceptación

**Métricas:** event lag, duplicates prevented, replay correctness, DLQ rate.

- Baseline determinista y escenarios sintéticos con resultado esperado.
- Unit tests, contract tests, integration tests, property tests y fault injection.
- Evaluación de carga, límites de concurrencia, saturación y errores de red.
- Idempotencia de efectos externos, autenticación, autorización y secretos fuera de logs.
- Reproducción de incidentes, rollback y trazabilidad de entradas, salidas y versiones.
- Benchmark con IC y comparación por carga, no una única corrida.

## 6. Entregables y gates

D1 arquitectura y amenaza; D2 contratos y modelo formal; D3 implementación; D4 pruebas y benchmarks; D5 validación independiente; D6 operación y runbook. G0 diseño → G1 modelo → G2 tests → G3 stress → G4 revisión → G5 operación. **D3–D6 pendientes**.

[Fundamentos compartidos](../fundamentals/README.md).
