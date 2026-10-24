# MVP — certificado geométrico de firma truncada

- **Qué es:** firma de nivel 2 de caminos poligonales finitos, con identidades algebraicas y benchmark sintético de orden/aliasing.
- **Cómo:** Python 3.12, `bash run.sh` desde esta carpeta.
- **Produce:** `results/replicates.csv`, `convergence.csv`, `scalability.csv`, `summary.json`, `audit.png`, cobertura y notebook con outputs ejecutados.
- **No cubre:** reconstrucción, rough-path lift de procesos estocásticos, clasificación real, firma de niveles superiores, validación operacional.
- **Madurez:** componente S2; el programa general sigue sin evidencia externa. S2 no se convierte automáticamente en M2.
- **Ejecución del notebook:** IPython in-process por restricción de sockets Jupyter, registrada en metadata. Código real secuencial; no se afirma prueba de kernel separado.
- **Entorno:** dependencias fijadas en requirements.txt; Linux x86_64 Python 3.12.14. `python -m venv .venv && source .venv/bin/activate` crea aislamiento opcional antes del comando.
