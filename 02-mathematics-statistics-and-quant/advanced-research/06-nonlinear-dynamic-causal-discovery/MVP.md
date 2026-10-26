# MVP de falsación de inferencias causales desde asociación temporal

- **Qué es:** generador SCM lineal gaussiano, test OLS anidado y auditoría de confusión omitida, lag erróneo y proxy con error.
- **Cómo:** `bash run.sh` desde esta carpeta con Python3.12; crea entorno aislado y usa requirements.txt fijado.
- **Produce:** notebook.ipynb ejecutado, results/replicates.csv, summary.csv/summary.json, audit.png, tests y cobertura; guarda seeds, n, β y recursos por ajuste.
- **No cubre:** nonlinearidad, feedback, errores autocorrelacionados, confusores latentes resueltos automáticamente, selección de lags, PCMCI, datos reales o causalidad operacional.
- **Interpretación:** el oráculo interventional sigue un SCM conocido; no valida identificación desde observaciones reales. Asociaciones omitidas no son falsos positivos respecto a su propia nulidad predictiva.
- **Madurez:** componente S2 limitado; programa06 no está completo y no se certifica S3/S4 ni M2.
- **Entorno reproducible:** Python3.12, Linuxx86_64, pins completos. Notebook ejecutado realmente con IPython en proceso y namespace fresco; no se declara ejecución con kernel separado.
