# Cuantitativo y ciencia de datos

Machine learning, deep learning, econometría y modelado estocástico aplicados a finanzas.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Regularización: OLS, Ridge y Lasso](regularizacion-ridge-lasso) | Comparación de mínimos cuadrados, Ridge y Lasso en un problema con 60 variables de las que solo 6 importan. | Laboratorio controlado · aplicación observada pendiente |
| [Gradient boosting frente a regresión logística](gradient-boosting-vs-logit) | Comparación de una regresión logística y un modelo de gradient boosting en un problema con interacciones no lineales: AUC, Brier score y diferencia de desempeño entre un caso lineal y uno no lineal. | Laboratorio controlado · aplicación observada pendiente |
| [Pronóstico con ARIMA y selección por AIC](arima-pronostico) | Laboratorio controlado y aplicación SARIMA al IPC observado de DANE, con selección por AIC, holdout cronológico y benchmark ingenuo estacional. | Laboratorio + aplicación observada |
| [Valoración de opciones: Monte Carlo y Black-Scholes](monte-carlo-opciones-black-scholes) | Valoración de una opción call europea con Black-Scholes en forma cerrada y con Monte Carlo (con y sin variables antitéticas), error estándar, convergencia con el número de trayectorias y delta por derivada pathwise. | Laboratorio controlado · aplicación observada pendiente |
| [Validación cruzada temporal y fuga de información](validacion-cruzada-temporal) | Conserva una demostración de fuga temporal sintética y compara KFold aleatorio con TimeSeriesSplit sobre inflación mensual observada de DANE. | Laboratorio + aplicación observada |
| [Análisis factorial múltiple (MFA)](analisis-factorial-multiple-mfa) | Laboratorio controlado más aplicación WDI observada: ejes, contribuciones de temas, cobertura, clusters y robustez. | Funcional · laboratorio + aplicación oficial |

Cada proyecto trae su notebook y, salvo el análisis factorial múltiple, su `main.py` ejecutable. Las aplicaciones observadas tienen runner, snapshot/hash, métricas y limitaciones propios; no sustituyen los laboratorios controlados ni implican validación institucional o productiva.
