# MVP
Qué: resumen escalar estable y fusionable para varianza de streams finitos. Comando: `bash run.sh` desde esta carpeta. Produce CSV/JSON/PNG, notebook con outputs, tests/cobertura/lint/tipos. Hipótesis local error<=1e-10 para offsets<=1e12 y fixture mod4 verificada. No cubre overflow, entradas originales perdidas por redondeo, distribución empírica ni varianza ponderada. Umbral no es garantía universal.

##30: extensión ejecutada
Mismo comando bash run.sh, añade src/scaled.py, tests/test_scaled.py, notebook_scale.ipynb y results/scale_raw.csv/scale_summary.json/scale_audit.png. Decisión continuar como adaptador de unidades con escala declarada. No sustituye NumPy ni recupera información perdida por redondeo; no cambio automático de escala. Varianza no representable se indica explícitamente, no como0/inf exitoso.
