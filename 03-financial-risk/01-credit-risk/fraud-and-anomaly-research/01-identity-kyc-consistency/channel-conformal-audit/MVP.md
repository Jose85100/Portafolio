# MVP

- Qué es: auditoría de alertas sobre scores fijos con rangos conservadores por canal.
- Cómo corre: `bash run.sh` desde esta carpeta, Python 3.12.
- Qué produce: 1.440 filas de ensayos agregados por semilla, summary.csv, metrics.json, audit.png, tests/cobertura/lint/tipos y notebook ejecutado.
- No cubre: entrenamiento de score KYC, etiquetas reales, autenticación de identidad, estimación de fraude, política de aprobación, FDR de lote, deriva corregida ni validez condicional individual.
- Madurez: prototipo sintético verificable del componente; revisión independiente del ciclo separada; ningún dominio completo se certifica M2/M3.
- Datos: generados, no hay clientes ni datos externos. Decisión admisible: investigar la calibración por canal antes de diseñar un piloto humano.
