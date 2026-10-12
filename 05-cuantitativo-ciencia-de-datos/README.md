# Cuantitativo y ciencia de datos

Machine learning, deep learning, econometría y modelado estocástico aplicados a finanzas.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Regularización: OLS, Ridge y Lasso](regularizacion-ridge-lasso) | Comparación de mínimos cuadrados, Ridge y Lasso en un problema con 60 variables de las que solo 6 importan. | Funcional · datos sintéticos |
| [Gradient boosting frente a regresión logística](gradient-boosting-vs-logit) | Comparación de una regresión logística y un modelo de gradient boosting en un problema con interacciones no lineales: AUC, Brier score y diferencia de desempeño entre un caso lineal y uno no lineal. | Funcional · datos sintéticos |
| [Pronóstico con ARIMA y selección por AIC](arima-pronostico) | Pronóstico de una serie con tendencia y estacionalidad: selección de orden ARIMA por AIC en una malla, validación en un tramo reservado y comparación contra un pronóstico ingenuo estacional. | Funcional · datos sintéticos |
| [Valoración de opciones: Monte Carlo y Black-Scholes](monte-carlo-opciones-black-scholes) | Valoración de una opción call europea con Black-Scholes en forma cerrada y con Monte Carlo (con y sin variables antitéticas), error estándar, convergencia con el número de trayectorias y delta por derivada pathwise. | Funcional · datos sintéticos |
| [Validación cruzada temporal y fuga de información](validacion-cruzada-temporal) | Demostración de por qué la validación cruzada aleatoria es engañosa en series de tiempo: sobre una serie persistente sin poder predictivo real, la validación aleatoria reporta un R² alto, mientras la validación temporal muestra el desempeño verdadero. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
| [Análisis factorial múltiple (MFA)](analisis-factorial-multiple-mfa) | MFA con datos reales del Banco Mundial: ejes, planos, clusters y robustez. | Funcional · datos reales abiertos |
