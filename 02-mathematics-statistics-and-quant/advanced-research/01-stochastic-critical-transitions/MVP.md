# Contrato del MVP

**Qué es:** auditoría ejecutable OU escalar de discretización e identificación. Programa 01 pasa de S1 a S2 únicamente para este alcance. Fecha: 2026-10-17. Base revisada: `931aa473062f70a55c58c73bc56aaada23564ff4`.

**Cómo corre:** Python 3.12, make y acceso a PyPI; `make run` desde esta carpeta instala dependencias y reproduce tests, benchmark, informe y notebook. Instrucciones de entorno en README.md. No servicios externos durante la simulación.

**Qué produce:** 84 corridas de exacto/Euler, 3.200 episodios estacionarios, 20 verificaciones contra exponencial matricial, CSV/JSON, figura PNG, ejemplos NPZ, tests y cobertura medida, notebook con outputs y un informe crítico. La ejecución falla si no se cumplen los umbrales de config.json. No se garantiza identidad de tiempos ni bytes del notebook entre máquinas.

**Baseline:** Euler en siete pasos, incluyendo uno fino y dos sin estacionariedad; misma muestra y Gaussianas estandarizadas dentro de cada comparación. Van Loan como referencia numérica independiente. Varianza poblacional aislada frente a información serial: contraejemplo, no competencia de modelos predictivos calibrados.

**Qué NO cubre:** saddle-node/pitchfork, ruido multiplicativo o coloreado, detector de crisis, CUSUM, pronóstico de colapso, causalidad, parámetros no estacionarios, aplicaciones con datos públicos o financieros. No se afirma que OU o la discretización exacta sean nuevos. No se modifica quant-libraries ni su contrato EL=83.

**Checklist:** src ejecutable; comando único; tests; baseline numérico; CSV/JSON/figura; README/informe/BibTeX/MVP; notebook ejecutado y estructura en la subcarpeta correcta. Los logs y archivos crudos son la evidencia, no esta declaración.
