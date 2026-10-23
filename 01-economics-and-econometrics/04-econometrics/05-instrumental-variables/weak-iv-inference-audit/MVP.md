# MVP: inferencia IV débil

- Qué es: auditoría reproducible de tests puntuales Anderson–Rubin y Wald convencional bajo un instrumento y regresor endógeno.
- Cómo corre: `bash run.sh` desde esta carpeta (Python 3.11+, venv y acceso a PyPI).
- Qué produce: 12.000 decisiones con semilla, tasas de rechazo y errores MC, figura, costes por método/tamaño, tests y notebook ejecutado.
- Qué no cubre: validación empírica, heteroscedasticidad, autocorrelación, instrumentos múltiples, intervalos invertidos ni explotación operacional.
- Madurez: S2 local. No se afirma S3, S4 ni madurez del programa completo; revisión independiente a cargo del revisor del ciclo.
- Hipótesis: en escenarios válidos, AR dentro de 5% ±2 puntos; la distorsión absoluta de Wald en c=1 supera la de AR al menos 5 puntos. Exclusión inválida es falsación negativa predefinida.
