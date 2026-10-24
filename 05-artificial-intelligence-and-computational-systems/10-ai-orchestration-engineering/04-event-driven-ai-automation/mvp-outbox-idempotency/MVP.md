# MVP y límites

- Qué es: relay outbox hacia proveedor idempotente en SQLite independiente con huella de intención.
- Corre: `bash run.sh` (Python3.12 + pip) desde esta carpeta.
- Produce: nueve tests, 144 lotes CSV, 18 resúmenes JSON, figura SVG y notebook ejecutado.
- No cubre: APIs que no implementan recibo atómico, TTL, red/broker real, energía/disco corrupto, garantías de orden, fencing o autenticar requests.
- Prototipo S2 del componente (antes diseño S1); M2 local candidato sujeto a revisión. No operacional.
- La prueba multiproceso mata un worker tras commit; no implica validación de cualquier corte posible de energía.
