# MVP — Replay bitemporal de vínculos incrementales

Pregunta: ¿el gate de historial completo del 3-nov puede procesar deltas sin confundir fecha efectiva con fecha de llegada?

Hipótesis falsable: para un ledger delta sin empates conflictivos, reproducir por máximo `effective_at` entre eventos conocidos al `cutoff` recupera exactamente el estado oráculo; el orden físico del archivo no cambia el resultado. El baseline `snapshot_first` ordena por llegada, falla cuando llega tarde una corrección de una vigencia anterior.

Original: el MVP temporal previo acepta snapshots completos y elige la revisión conocida más reciente antes de validar su intervalo. Extensión: cada cambio se representa como `(edge, action, effective_at, available_at, event_id)`; se filtra por `available_at <= cutoff` y `effective_at <= identity_at`, y se conserva por arista la acción de mayor `effective_at`. Empates contradictorios y event_id duplicado producen abstención por excepción. No hay demostración sobre fuentes externas: la semántica se define aquí y se verifica con oráculo sintético.

Candidatas evaluadas: extender full-replacement (no resuelve deltas); ledger intervalar no solapado (exige migración amplia); replay incremental bitemporal (seleccionada, reutiliza el gate y tiene contraejemplo concreto).

Reproducir: `bash run_delta_audit.sh` en esta carpeta. Genera `results/delta1104/raw.csv`, `summary.json`, `replay_cost.png`, notebook ejecutado y logs. Dataset: sintético determinista; semilla 1104, 1–1000 aristas, tres eventos/arista. Python/dependencias fijadas en `requirements.txt`; hardware reportado en `results/delta1104/environment.json`.

Limitaciones: no autentica marcas temporales, no valida identidad verdadera, no cubre correcciones que requieran recomputar estados posteriores con reglas distintas, ni demuestra reducción de leakage en un pipeline de entrenamiento. Reproducción pedagógica/adaptación de ingeniería; no nueva metodología científica. Estado: M1 incremental local, no validado, no operacional.
