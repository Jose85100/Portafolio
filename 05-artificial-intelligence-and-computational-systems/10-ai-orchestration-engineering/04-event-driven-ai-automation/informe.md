# Informe de I+D+i — 2026-10-14

## Pregunta, hipótesis y brecha

¿Un inbox transaccional con clave de idempotencia y recuperación produce efectos locales correctos tras entregas repetidas y fallos, y a qué costo? Hipótesis falsable: error de suma y delta de replay iguales a cero; penalización de latencia/memoria positiva frente al consumidor ingenuo. La especificación S1 del repositorio carecía de motor ejecutable.

## Prior art

Helland (CIDR 2007) discute límites de transacciones distribuidas; Carbone et al. (arXiv:1506.08603) presentan snapshots; Trofimov et al. (arXiv:1907.06250) formalizan garantías; Kleppmann (2017) trata consistencia; Kafka y Debezium documentan transacciones y outbox. Ver siete fuentes en `referencias.bib`. Ninguna autoriza a extrapolar transacciones SQLite a exactly-once de efectos externos.

## Diseño y supuestos

30 seeds (0–29), 120 IDs base por workload, 3 regímenes (duplicados 10/60/30%; fallos 10/15/60%), conflictos 5%, inválidos 5%, 3 políticas = 270 corridas pareadas. Los eventos se barajan; el oráculo toma el primer payload válido por ID. Un fallo inyectado provoca rollback del efecto antes del commit; `inbox` reintenta pendientes. Se reentrega íntegramente la secuencia una vez. IC aproximado t(29) al 95% sin ajuste por múltiples comparaciones.

## Resultados de ejecución local (promedio de 30 semillas)

| Régimen | Política | Error absoluto de suma | Delta de replay |
|---|---|---:|---:|
| low_duplicate | naive | 1183.20 | 7494.77 |
| low_duplicate | inbox | **0** | **0** |
| low_duplicate | inbox_no_retry | 610.43 | 0 |
| burst_duplicate | naive | 4264.67 | 10492.90 |
| burst_duplicate | inbox | **0** | **0** |
| burst_duplicate | inbox_no_retry | 952.57 | 0 |
| high_fault | naive | 2474.30 | 8699.20 |
| high_fault | inbox | **0** | **0** |
| high_fault | inbox_no_retry | 3740.30 | 0 |

Los valores por corrida se generan en `results/raw.csv`, los promedios, IC y entorno en `results/summary.json`, y la figura en `results/error_by_regime.svg`. Las latencias y tiempos de proceso dependen del hardware y del `tracemalloc` activo; no son latencias de red.

## Análisis crítico y ablaciones negativas

El baseline aplica duplicados y conflictos como efectos nuevos; por eso falla el oráculo y el replay. La ablación `inbox_no_retry` evita duplicados pero deja eventos pendientes y falla ante inyección de fallos. El inbox completo alcanza error cero en las 90 combinaciones de régimen/seed, pero añade operaciones SQLite y más latencia/memoria. La comparación de rendimiento no es equitativa en durabilidad: el baseline no persiste nada. No hay prueba de superioridad de throughput frente a Kafka Streams, Flink ni otro consumidor durable.

## Tests, cobertura y limitaciones

Se ejecutaron localmente 14 tests (incluido test aleatorizado de 20 seeds) sobre la implementación de referencia; cobertura branch+statement combinada del motor y experimento: 95% con `coverage.py`. El conjunto del PR contiene tests de contratos y recuperación; la CI debe confirmar su ejecución. La reproducción remota genera el benchmark de nuevo.

Riesgos pendientes: autenticación de productores, colisiones maliciosas de IDs, acceso a SQLite, retención y crecimiento del inbox/DLQ, concurrency, backups, locks, multiworker, schema evolution, orden causal, trazabilidad y efectos externos. No se procesan datos personales: los datos son sintéticos. No hay evaluación independiente, datos operativos, broker ni LLM. Madurez **M2 local**, no operacional.
