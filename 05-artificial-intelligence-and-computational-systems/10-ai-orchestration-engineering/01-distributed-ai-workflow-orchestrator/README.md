# Distributed AI Workflow Orchestrator

**Estado:** S1 — diseño verificable, no motor implementado.

## 1. Mandato, decisión y pregunta

Ejecutar grafos acíclicos de tareas de IA con dependencias, presupuestos y control de concurrencia.

**Pregunta falsable:** ¿el diseño propuesto mejora makespan, throughput, p95, costo por workflow, task success frente a un baseline simple y reproducible sin introducir fallos de seguridad, integridad o costo?

## 2. Modelo matemático

G=(V,E) DAG; min_σ makespan(σ) sujeto a precedencia, CPU, GPU y cuotas; critical path lower bound.

Definir formalmente estados, eventos, transiciones, decisiones, restricciones, dominio, horizonte y unidades. Demostrar invariantes, condiciones de terminación y límites de validez. No asumir independencia ni atomicidad de servicios distribuidos sin justificación.

## 3. Modelado estadístico

Tiempos de servicio no estacionarios, bootstrap de p95, distribución de makespan y escenarios de carga. Estimar incertidumbre, dependencia, percentiles de cola y estabilidad entre cargas; registrar tamaños muestrales, seeds, hardware y entorno.

## 4. Arquitectura de implementación

Python scheduler y API; C++20 algoritmo DAG; Redis/NATS opcional; PostgreSQL.

**Diseño de carpetas futuro:** `contracts/`, `cpp/`, `python/`, `sql/`, `tests/`, `experiments/`, `security/`, `docs/`. Versionar contratos de eventos y decisiones; separar plano de control y plano de ejecución.

## 5. Pruebas y aceptación

**Métricas:** makespan, throughput, p95, costo por workflow, task success.

- Baseline determinista y escenarios sintéticos con resultado esperado.
- Unit tests, contract tests, integration tests, property tests y fault injection.
- Evaluación de carga, límites de concurrencia, saturación y errores de red.
- Idempotencia de efectos externos, autenticación, autorización y secretos fuera de logs.
- Reproducción de incidentes, rollback y trazabilidad de entradas, salidas y versiones.
- Benchmark con IC y comparación por carga, no una única corrida.

## 6. Entregables y gates

D1 arquitectura y amenaza; D2 contratos y modelo formal; D3 implementación; D4 pruebas y benchmarks; D5 validación independiente; D6 operación y runbook. G0 diseño → G1 modelo → G2 tests → G3 stress → G4 revisión → G5 operación. **D3–D6 pendientes**.

[Fundamentos compartidos](../fundamentals/README.md).
