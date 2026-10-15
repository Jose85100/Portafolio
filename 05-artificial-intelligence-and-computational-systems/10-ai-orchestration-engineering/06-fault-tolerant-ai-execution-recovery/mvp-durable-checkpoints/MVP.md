# Declaración de MVP y madurez

**Qué es:** demostrador reproducible de recuperación de dos pasos con SQLite, inyección de fallos, checkpoints transaccionales y deduplicación de efectos locales.

**Cómo se corre:** `bash run.sh` desde cualquier directorio (el script se posiciona en su carpeta).

**Qué produce:** pruebas ejecutadas, CSV de 24 corridas, JSON con medias e IC descriptivos, figura SVG; sin datos privados.

**Qué NO cubre:** procesos concurrentes, APIs remotas, Kafka, semántica exactamente-una-vez end-to-end, sagas distribuidas, compensaciones, LLMs, fallos del sistema operativo, apagones físicos, benchmarks de throughput real, validación independiente, seguridad de producción.

**Madurez:** M2 de este **componente local** solo si sus pruebas y artefactos pasan en el entorno de reproducción. No elevar todo el proyecto S1 ni el dominio 05 a M2. No es M3 ni producto operacional.

**Garantía demostrada:** un efecto escrito y su checkpoint son atómicos **dentro de una única base SQLite**; el índice único protege contra replays. La validez externa requiere nuevos experimentos.
