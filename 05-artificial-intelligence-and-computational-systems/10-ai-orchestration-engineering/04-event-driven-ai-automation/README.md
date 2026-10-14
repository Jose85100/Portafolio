# Event-Driven AI Automation Platform

**Madurez:** M2 — prototipo local verificado, NO plataforma operacional.

## Mandato y brecha S1

Procesar eventos de negocio y disparar workflows con garantías explícitas de entrega e idempotencia. La especificación S1 no contenía código. El MVP cubre solamente efectos locales SQLite: inbox, idempotencia por event_id, rechazo de payloads conflictivos, DLQ de mensajes inválidos, recuperación y replay. Kafka/NATS, outbox, autenticación y side effects externos quedan fuera.

## Comando único de reproducción

Desde esta carpeta, con Python 3.11+:

```bash
bash reproduce.sh
```

No requiere internet ni dependencias externas. Ejecuta los tests y 270 simulaciones (30 seeds x 3 regímenes x 3 políticas), y genera `results/raw.csv`, `results/summary.json` y `results/error_by_regime.svg`. Alternativa: `docker build -t event-inbox . && docker run --rm event-inbox`.

## Diseño experimental

Cada secuencia tiene 120 eventos base; duplicados 10/30/60%, conflictos 5%, inválidos 5%, fallos inyectados 10/15/60% según régimen. Se evalúan `naive` (sin deduplicación), `inbox` (persistencia y recuperación) e `inbox_no_retry` (ablación negativa). El mismo workload se usa en las tres políticas y luego se reentrega íntegramente. Se mide error absoluto contra oráculo first-valid, replay delta, pendientes, DLQ, p95 de entrega local, tiempo y memoria. IC t(29) aproximados; no se ajustan comparaciones múltiples.

## Archivos

`src/engine.py`: inbox SQLite; `src/experiment.py`: generador y baseline; `src/benchmark.py`: evaluación y figura; `tests/`: contratos, integridad y recuperación; `results/`: salidas; `informe.md`, `MVP.md`, `referencias.bib`: análisis, límites y prior art.

## Garantías y restricciones

La transacción atómica cubre exclusivamente el efecto escrito en la misma base SQLite. No existe garantía exactly-once para APIs, pagos, mensajes o servicios externos. No hay aislamiento multiworker, control de acceso, TTL, backpressure, pruebas de red ni validación independiente. Las pruebas sintéticas no constituyen evidencia operacional.

## Fundamentos compartidos

Consultar `../fundamentals/README.md` para modelos formales, estadística y diseño computacional. El proyecto sigue el estándar de madurez del repositorio y no altera `data-engineering/`.
