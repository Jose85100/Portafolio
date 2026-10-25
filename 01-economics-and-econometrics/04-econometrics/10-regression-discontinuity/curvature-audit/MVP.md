# MVP ejecutable: auditoría de discontinuidad local lineal

- Qué es: estimador sharpRD y comparación global/local bajo curvatura, reducción excesiva de ventana y fallo de continuidad.
- Comando: `bash run.sh` con Python3.11+, venv, PyPI.
- Produce:18.000 estimaciones crudas, RMSE/sesgo/SD y error Monte Carlo pareado, figura, coste por brazo/tamaño, notebook ejecutado y tests.
- Hipótesis previa: en DGP asimétrico válido, RMSEh0,2≤50% de RMSEglobalh1. Resultado0,08295/0,67192≈0,12345. No generalizar a otros DGP.
- Qué no cubre: inferencia RBC, identificación observacional, selecciónóptima bandwidth, fuzzy/discreto/clusters ni producción.
- Madurez:S2 del componente solamente; no equivale a M2 de otro estándar. Revisión independiente a cargo del revisor del ciclo.
