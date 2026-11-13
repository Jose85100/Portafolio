# MVP: estabilidad y calibración del posterior lineal gaussiano

**Qué es:** prototipo S2 del programa 08: inferencia analítica densa, benchmark
contra una referencia de alta precisión y diagnóstico separado de mala calibración.

**Cómo corre:** `make run` desde esta carpeta. Requiere Python 3.11+, make e
internet para instalar las dependencias fijadas. No requiere datos externos.

**Qué produce:** media y covarianza; CSV de precisión, costos y cobertura;
results.json; figura PNG; pruebas, cobertura, notebook realmente ejecutado y
reporte actualizado. El comando termina con error si el umbral predefinido falla.

**Qué NO cubre:** MCMC, Laplace no lineal, VI, priors no gaussianos, ruido
correlacionado, inferencia de hiperparámetros, mala especificación de A estimada,
garantías asintóticas ni calibración financiera. No se cambia el contrato EL=83
de quant-libraries. No se avanza a S3/S4 por este benchmark sintético.
