# MVP — Transactional Event Inbox and Replay Audit

- **Qué es:** consumidor Python/SQLite con inbox persistente, efecto local transaccional, deduplicación, validación, DLQ para inválidos, reintento y auditoría de replay.
- **Cómo se corre:** `bash reproduce.sh` desde esta carpeta. Python 3.11+ sin dependencias externas.
- **Qué produce:** tests, `results/raw.csv`, `results/summary.json`, `results/error_by_regime.svg`; 270 corridas sintéticas pareadas.
- **Qué NO cubre:** Kafka/NATS, efectos externos, outbox, TTL, multiworker, auth, datos reales, fallos de red ni evaluación independiente.
- **Madurez:** M2, prototipo verificado; no validado independientemente ni operacional. La implementación es local, no una plataforma distribuida.
