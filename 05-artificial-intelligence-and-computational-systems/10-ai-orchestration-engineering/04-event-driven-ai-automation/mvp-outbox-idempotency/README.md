# Outbox + recibo semántico ante ACK perdido

MVP de orquestación orientada a eventos: el emisor y el proveedor usan **dos archivos SQLite y transacciones independientes**. Se inyecta fallo después del commit del proveedor y antes del ACK del emisor. Un proveedor con clave idempotente y huella del payload evita duplicados y rechaza reutilizaciones de clave con intención distinta.

## Reproducir

Desde esta carpeta, Python 3.12 con pip:

```bash
bash run.sh
```

Instala requisitos de notebook fijados, ejecuta nueve tests (incluyendo proceso terminado con os._exit(77) y acceso concurrente al proveedor), 144 lotes pareados y notebook. El núcleo sólo usa biblioteca estándar. En entorno ya preparado: `PYTHON=/ruta/python SKIP_INSTALL=1 bash run.sh`. Los datos son sintéticos, no hay claves/API ni conexión a proveedores reales.

## Diferencia respecto a código previo

`06-fault-tolerant-ai-execution-recovery/mvp-durable-checkpoints` demuestra efecto y checkpoint en la misma SQLite. Aquí **no existe commit conjunto entre emisor y proveedor**. El fallo ambiguo se resuelve mediante un contrato que el proveedor realmente implementa: recibo y efecto en su propia transacción. No se afirma exactamente-una-vez para APIs arbitrarias ni red real. La novedad es incremental de integración y falsificación del contrato, no invención del patrón outbox.

## Contratos

- `no_dedup`: baseline de al menos una entrega, efecto repetido por retry.
- `key_only`: deduplica, pero reutilizar la clave con payload cambiado devuelve resultado previo silenciosamente.
- `key_hash`: recibo `(key, SHA256(payload_canónico), effect_id)` y efecto se confirman atómicamente en proveedor; conflicto de intención produce `PayloadConflict` sin nuevo efecto.
- Emisor almacena job y outbox en una transacción local. Nunca ACK antes del commit del proveedor.
- Claves deben estar namespaced por tenant/operación y la política debe permanecer fija para cada almacenamiento. La huella no autentica al cliente.

## Evidencia y madurez

Resultados y recursos por lote en `results/raw.csv` y `results/summary.json`; figura `results/duplicates.svg`, notebook ejecutado e `informe.md` con 14 puntos. Ocho semillas, tamaños20/100, pérdidas ACK0/0.35/0.8, presupuesto8 intentos.

Componente S2 ejecutado, candidato M2 local sujeto a revisión técnica; el pilar completo sigue parcial. Sin TTL ni borrado de recibos, orden global, concurrencia del emisor distribuido, fencing, autenticación, Kafka, red real, cortes de energía ni operación productiva. Un presupuesto finito permite outbox pendiente aunque el efecto exista: entrega completada no equivale a efecto aplicado.
