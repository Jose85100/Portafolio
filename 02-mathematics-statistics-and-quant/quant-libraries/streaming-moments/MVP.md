# MVP
Qué: resumen escalar estable y fusionable para varianza de streams finitos. Comando: `bash run.sh` desde esta carpeta. Produce CSV/JSON/PNG, notebook con outputs, tests/cobertura/lint/tipos. Hipótesis local error<=1e-10 para offsets<=1e12 y fixture mod4 verificada. No cubre overflow, entradas originales perdidas por redondeo, distribución empírica ni varianza ponderada. Umbral no es garantía universal.

##30: extensión ejecutada
Mismo comando bash run.sh, añade src/scaled.py, tests/test_scaled.py, notebook_scale.ipynb y results/scale_raw.csv/scale_summary.json/scale_audit.png. Decisión continuar como adaptador de unidades con escala declarada. No sustituye NumPy ni recupera información perdida por redondeo; no cambio automático de escala. Varianza no representable se indica explícitamente, no como0/inf exitoso.

## Incremento31: autoescala y subnormales
`bash run.sh` conserva29/30 y reproduce31. API `src.dynamic.dynamic_moments(values, ddof=0)` consume iterable una vez; `DynamicMoments.push` permite inspeccionar estado y pérdidas detectadas. Ver notebook_dynamic.ipynb, derivacion_dynamic.md, informe_dynamic.md, config_dynamic.json y prior_art_dynamic.md. Salidas results/dynamic_raw.csv, dynamic_summary.json, dynamic_audit.png. No cubre merge dinámico, pesos, garantía universal de precisión o validación empírica. Prototipo local, no operacional.
