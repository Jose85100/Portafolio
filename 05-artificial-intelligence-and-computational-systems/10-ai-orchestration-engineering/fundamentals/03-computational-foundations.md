# III. Fundamento computacional y de sistemas

## Arquitectura de referencia

```text
API / Event Ingress
  → Authentication + Authorization + Quotas
  → Durable State / Event Log
  → Planner + Scheduler + Model Router
  → Task Queues + Worker Pools + Tool Sandbox
  → Checkpoint / Retry / Compensation
  → Traces + Metrics + Audit + Evaluation
```

## Ingeniería

- Python 3.12+: orquestación, contratos tipados, async IO, APIs, workers y evaluaciones.
- C++20: scheduling intensivo, colas, algoritmos de grafos y profiling donde el benchmark justifique complejidad.
- SQL/PostgreSQL: transacciones, outbox/inbox, locks, checkpoints, replay y lineage.
- NATS/Kafka/Redis: transportes opcionales con garantías específicas, sin prometer exactly-once para efectos externos.
- OpenTelemetry: traces con correlation IDs, métricas, logs sanitizados y presupuesto de cardinalidad.
- Docker/CI: tests unitarios, contract tests, fault injection, load tests, reproducibilidad y rollback.

## Contratos mínimos

`WorkflowSpec/v1`, `TaskEnvelope/v1`, `ExecutionState/v1`, `ToolPolicy/v1`, `ModelRouteDecision/v1`, `AuditEvent/v1`. Campos: tenant, workflow_id, task_id, attempt, idempotency_key, trace_id, deadline, budget, model_version, policy_version y timestamps.

## Seguridad

Zero-trust para herramientas, separación de permisos, control de secretos, límites de recursos, protección de PII, aprobaciones humanas para acciones irreversibles. Documentar failure modes y runbooks.
