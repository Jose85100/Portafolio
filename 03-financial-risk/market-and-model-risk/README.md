# Riesgo financiero y riesgo de modelos

Validación y documentación de modelos, pruebas de estrés, análisis de sensibilidad y escenarios macro-financieros.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [VaR y Expected Shortfall por tres métodos](var-es-tres-metodos) | Cálculo de VaR y Expected Shortfall de un portafolio con simulación histórica, método paramétrico normal y ajuste t de Student, sobre retornos con colas pesadas. | Funcional · datos sintéticos |
| [Backtesting de VaR: Kupiec y Christoffersen](backtesting-var-kupiec-christoffersen) | Backtesting de un VaR histórico al 99 % con ventana móvil sobre una serie con régimen de alta volatilidad. | Funcional · datos sintéticos |
| [Volatilidad GARCH y VaR condicional](garch-volatilidad-y-var) | Estimación de un GARCH(1,1) con t de Student sobre retornos simulados, comparación de los parámetros estimados con los verdaderos y VaR a un día condicional a la volatilidad pronosticada. | Funcional · datos sintéticos |
| [Pruebas de estrés y estrés inverso](pruebas-de-estres-escenarios) | Pruebas de estrés de un portafolio con sensibilidades lineales a factores (acciones, tasas, tipo de cambio, spreads de crédito). | Funcional · datos sintéticos |
| [Validación de modelo: Gini, calibración y PSI](validacion-de-modelo-psi-gini) | Validación independiente de un modelo de PD: comparación champion (regresión logística) contra challenger (gradient boosting), discriminación (Gini), calibración por deciles y estabilidad (PSI) entre desarrollo y muestra fuera de tiempo, con umbrales de alerta. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
