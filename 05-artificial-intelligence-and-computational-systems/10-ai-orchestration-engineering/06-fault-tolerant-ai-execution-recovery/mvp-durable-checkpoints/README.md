# Durable Checkpoints & Idempotent Recovery — MVP

**Pilar:** `10-ai-orchestration-engineering/06-fault-tolerant-ai-execution-recovery`.
**Madurez:** componente M2 local; el proyecto padre sigue S1 para las funcionalidades no implementadas. No es un sistema operacional.

## Reproducción (comando único)

```bash
bash run.sh
```

Requiere **Python 3.10+** y `sqlite3` integrado; sin red, credenciales, contenedores ni dependencias externas. `run.sh` ejecuta tests, verificación sintáctica y 24 benchmarks pareados (8 semillas × 3 políticas). Escribe `results/raw.csv`, `results/summary.json` y `results/duplicates.svg`.

## Pregunta e hipótesis

¿La actualización atómica del efecto local y su checkpoint evita efectos duplicados tras reinicios simulados, comparada con reejecución desde cero y checkpoints no atómicos?

H1: tasa de efectos duplicados de `atomic` = 0 en los escenarios simulados; `naive` y `split` > 0 cuando se inyectan fallos. H2: la integridad tiene un coste de latencia por job.

## Contrato

- Dos pasos deterministas `reserve → finalize`, ambos efectos son filas **locales** de SQLite.
- Se inyecta un único fallo por job, después de un efecto confirmado en disco; reanudación abre otra conexión.
- `naive`: reejecuta desde paso 0 sin checkpoint.
- `split`: escribe efecto y checkpoint en transacciones separadas; fallo entre ambas.
- `atomic`: escribe efecto y checkpoint en una transacción `BEGIN IMMEDIATE`, con índice UNIQUE `(job_id, step)`.
- Misma secuencia de fallos por semilla para las tres políticas. Los fallos son sintéticos, no señales del SO.

## Estructura

`src/engine.py` motor, `src/experiment.py` experimento/figura, `tests/` unitarias y aleatorizadas, `benchmarks/` ejecutor, `results/` evidencia, `informe.md` análisis crítico, `MVP.md` límites, `referencias.bib` prior art.

## Comandos auxiliares

```bash
python3 -m unittest discover -s tests -v
python3 -m src
python3 -m coverage run -m unittest discover -s tests && python3 -m coverage report -m  # opcional si coverage está instalado
```

No se afirma exactamente-una-vez para efectos externos, múltiples procesos, brokers, redes, sistemas distribuidos, ni ejecución de agentes LLM.
