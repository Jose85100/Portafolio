# MVP

- Qué: selector finito de precio con capacidad y presupuestoCVaR de pérdida positiva.
- Corre: `bash run.sh`; entorno preparado `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- Produce: CSVmenú/sensibilidad/scaling/MC, summaryJSON, figura, notebook ejecutado, tests/cobertura.
- No cubre: elasticidad estimada, causalidad, ventas aleatorias individuales, pricing dinámico, efectos de competencia, inversión de capacidad.
- Madurez: componenteS2 sintético; no equivale automáticamenteM2 ni acredita programa09.
- Decisión: continuar piloto de precio18 si supuestos/costos válidos; ajustar ante nuevos escenarios/costos; detener si ningún precio crea valor respetando presupuesto.
- Checklist: código✓ comando✓ test✓ baseline✓ salida✓ notebookoutputs✓ referencias5✓ informe✓ README/MVP✓ entorno✓ carpeta09✓. Revisión independiente y publicación PR se reportan separadas de ejecución.
