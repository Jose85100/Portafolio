# MVP: auditor temporal de reemplazos de identidad

**Qué es.** Selector tipado e in-memory para historiales sintéticos con reemplazo completo: toma la revisión de mayor `available_at` conocida al cutoff y verifica si es válida en `identity_at`.

**Comando reproducible:** desde esta carpeta, `bash run_temporal_revisions.sh`. Instala `requirements.txt` en `.venv`, ejecuta regresiones más el incremento, Ruff/mypy, experimentos CSV/JSON y notebook ejecutado. Si el entorno ya tiene deps: `SKIP_INSTALL=1 PYTHON=.venv/bin/python bash run_temporal_revisions.sh`.

**Salidas:** `results/temporal1103/raw.csv.gz` (CSV crudo gzip), `summary.json`, `counterexample.json`, `cost.json`, `environment.json`, `admissions.png`, logs, `notebook_temporal1103.ipynb` con outputs; fórmula y límites en `derivacion_temporal1103.md`.

**Madurez:** prototipo experimental sintético ejecutado; no validado contra ledger real, no operacional y no garantiza point-in-time de fuentes, entidades o feature pipelines. No trata eventos incrementales/deltas ni autentica la procedencia. La decisión sobre validez semántica del replacement pertenece al dueño de datos.
