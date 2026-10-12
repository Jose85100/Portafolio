# Gestión de portafolios

Optimización de portafolios, medición de riesgo y asignación sin ventas en corto.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Frontera eficiente de Markowitz](frontera-eficiente-markowitz) | Frontera eficiente long-only de cinco activos con optimización de varianza mínima para una malla de retornos objetivo, portafolio de mínima varianza global y portafolio de máximo Sharpe. | Funcional · datos sintéticos |
| [Portafolio de paridad de riesgo](paridad-de-riesgo) | Portafolio de paridad de riesgo (equal risk contribution) resuelto numéricamente. | Funcional · datos sintéticos |
| [Modelo Black-Litterman](black-litterman) | Combinación del equilibrio de mercado con opiniones del gestor mediante Black-Litterman: rendimientos implícitos de equilibrio, matriz de opiniones con incertidumbre, retornos posteriores y pesos resultantes. | Funcional · datos sintéticos |
| [Backtest de rebalanceo con costos de transacción](backtest-rebalanceo-con-costos) | Backtest de diez años con retornos simulados que compara pesos iguales y mínima varianza con covarianza móvil, rebalanceo mensual y costos de transacción proporcionales a la rotación. | Funcional · datos sintéticos |
| [Métricas de desempeño y atribución](metricas-de-desempeno-y-atribucion) | Biblioteca de métricas de desempeño de un portafolio frente a su benchmark: retorno anualizado, volatilidad, Sharpe, Sortino, máximo drawdown, Calmar, alfa y beta por regresión, tracking error e information ratio. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
