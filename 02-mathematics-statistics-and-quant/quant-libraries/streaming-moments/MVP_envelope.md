# MVP: envelope lateral de auditoría

- **Qué es:** metadatos declarativos de procedencia y disponibilidad de diagnósticos sobre un payload MOMENTS_V1 sin cambiar su wire.
- **Comando:** `bash run.sh` (requiere Python 3.12, dependencias fijadas y compilador C++20; alternativa: `MATH_ENV=/ruta/venv`).
- **Salidas:** `results/envelope_raw.csv`, `envelope_summary.json`, `envelope_audit.png`, `notebook_envelope.ipynb`, logs de test/lint/tipos/CTest.
- **Qué prueba:** preservación exacta de payload y status tracked/partial/unknown, rechazo de mutaciones de payload/metadatos y validación semántica de contadores.
- **Qué no cubre:** firma/autenticidad, disjunción real de particiones, procedencia confiable, integridad de filas originales, canonicalización JCS, almacenamiento o validación de un productor externo.
- **Madurez:** prototipo matemático/ingeniería ejecutado; no operacional, no ascenso automático a M2/S2 del programa.
