# Programa acumulativo: momentos reproducibles

|Fecha|Pregunta/decisión|Evidencia durable|Negativo aprendido|Madurez|
|---|---|---|---|---|
|2026-10-29|¿Evitar cancelación por offset y fusionar?|PR101; src/moments.py, notebook.ipynb, results/raw.csv|NumPy exacto en fixtures; a1e16 datosya redondeados; extremos finitospuedenoverflow|Prototipo verificado local|
|2026-10-30|¿SD representable cuando varianza no cabe?|src/scaled.py; notebook_scale.ipynb; results/scale_raw.csv; PR enlazado en entrega|Escala mala rechazada; NumPy+mismaescala más preciso/rápido; no recuperar señalperdida|Prototipo acumulativo, no operacional|

## Selección de tres ideas30
1 Pesos arbitrarios: útil pero exige definir ddof/semántica; aplazar para no diluir cierre.
2 Sólo RSS/timing: mejora evidencia29 pero no cierra overflow; incorporar5repeticiones y memoria separada como apoyo.
3 Unidad binaria externa y estados explícitos: elegida; cierra brecha29 sin nueva carpeta ni contrato compartido global.

## Roadmap con gates
1 src/scaled.py: escala dinámica y merge entre escalas sólo tras prueba de invariantes y pérdida informativa; mantener rechazo mixto como control.
2 src/benchmark_scale.py: ordenes/distribuciones y límites subnormales; gate falsable: ningún éxito con SD0 si oráculoSD>0representable.
3 config_scale.json/results: repeticiones30+,RSS de procesos separados y distribución de timings antes de presupuesto de rendimiento. No prometido/ejecutado todavía.

Continuar adaptador explícito; ajustar ante normalization_failure; cerrar afirmación de superioridad universal. No ascenso de programasadvanced-research, sin equivalencia automáticaS2/M2. Nuevo lenguaje no justificado: núcleo simplePython; cross-tests EL83 existentes se conservan sin cambios.
