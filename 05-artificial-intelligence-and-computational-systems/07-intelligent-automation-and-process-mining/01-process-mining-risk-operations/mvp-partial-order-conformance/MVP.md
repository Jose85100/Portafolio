# MVP

- Qué es: auditor exacto acotado de orden parcial para referencia secuencial única.
- Comando: `bash run.sh` desde esta carpeta con Python 3.12+pip.
- Produce:10 tests,1.200 trazasJSONL,3.600 comparacionesCSV,18 resúmenes y 7 perfiles de escala, figuraSVG y notebook ejecutado.
- No cubre: Petri nets/BPMN, concurrencia de proceso, desfase entre relojes, logs empíricos, parserXES, causalidad ni reparación de timestamps.
- Madurez: componenteS2 antes propuestaS1; candidatoM2 local con revisión técnica pendiente, no operacional.
- Semántica: uncertain order devuelve ambiguous; exceso de recursos devuelve budget_exceeded con lower/upperNone. Ninguno equivale a conformidad demostrada.
