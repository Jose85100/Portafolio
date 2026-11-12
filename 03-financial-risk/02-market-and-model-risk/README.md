# Riesgo financiero y riesgo de modelos

Validación y documentación de modelos, pruebas de estrés, análisis de sensibilidad y escenarios macro-financieros.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [VaR y Expected Shortfall](var-es-tres-metodos) | Laboratorio controlado de estimadores más aplicaciones con cambios oficiales de tasa del Tesoro EE. UU. y TES COP de BanRep, traducidos a pérdidas proxy por duración fija. | Funcional · edición de método y proxies observadas; P&L institucional pendiente |
| [Backtesting de VaR: Kupiec y Christoffersen](backtesting-var-kupiec-christoffersen) | Pruebas de cobertura e independencia sobre régimen controlado y choques del Tesoro EE. UU./TES COP de BanRep convertidos en P&L proxy. | Funcional · laboratorio + aplicación observada; cartera pendiente |
| [Volatilidad GARCH y VaR condicional](garch-volatilidad-y-var) | Recuperación de parámetros en laboratorio controlado y aplicación GARCH-t al factor oficial de tasa, con pronóstico y backtest fuera de tiempo. | Funcional · laboratorio + aplicación observada |
| [Pruebas de estrés y estrés inverso](pruebas-de-estres-escenarios) | Laboratorio multifactor y contraste de pérdidas por shocks oficiales de tasa, con estrés inverso de un factor. | Funcional · laboratorio + aplicación observada |
| [Validación de modelo: Gini, calibración y PSI](validacion-de-modelo-psi-gini) | Laboratorio sintético de discriminación/calibración más un [PSI observado de mezcla SFC A–E](validacion-de-modelo-psi-gini/observed-sfc-grade-composition), que no es drift de score. | Laboratorio + proxy descriptivo · Gini, calibración y PSI de score requieren scores y outcomes crediticios autorizados |
| [Auditoría de ES ponderado](weighted-expected-shortfall-audit/) | ES de masa fraccionaria con probabilidades desiguales, oráculo LP, auditoría de tres baselines y [Treasury EE. UU.](weighted-expected-shortfall-audit/observed-treasury-rate-proxy/) y [TES COP de BanRep](weighted-expected-shortfall-audit/observed-colombian-tes-rate-proxy/) como factores para P&L proxy por duración. | Auditoría numérica + proxies de P&L por duración · aplicación de cartera pendiente |
| [Guard Python contra underflow en ES](weighted-tail-underflow-guard/) | Detección NumPy, rechazo o fallback racional, flags de representabilidad y comparación con el baseline real. | Auditoría numérica · aplicación de cartera pendiente |

Cada proyecto trae código ejecutable y evidencia correspondiente a su alcance. Las etiquetas distinguen experimentos de método, datos observados y validación de aplicación.
