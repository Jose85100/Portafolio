# Riesgo de crédito: estrategia y portafolio

Visión de cartera: concentración, correlación de incumplimientos, apetito de riesgo y decisiones de asignación de crédito.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Concentración de cartera con HHI](concentracion-hhi-cartera) | Medición de concentración por deudor y por sector con el índice Herfindahl-Hirschman, número efectivo de contrapartes, participación de los mayores deudores y comparación con límites de apetito. | Funcional · datos sintéticos |
| [Capital de Vasicek frente a Monte Carlo](vasicek-perdida-no-esperada) | Fórmula de un factor de Vasicek (ASRF) para la pérdida no esperada al 99,9 % y su verificación con una simulación Monte Carlo de un portafolio homogéneo finito, con distintos niveles de correlación. | Funcional · datos sintéticos |
| [Distribución de pérdidas con cópula gaussiana](copula-gaussiana-perdidas) | Simulación de la distribución de pérdidas de una cartera heterogénea de 200 deudores con un modelo de factor común (cópula gaussiana). | Funcional · datos sintéticos |
| [Monitor de límites de apetito de riesgo](monitor-de-limites-de-apetito) | Tablero de límites de apetito: calcula utilización de cada límite por sector, rating y deudor y asigna un semáforo (verde, ámbar, rojo) con reglas explícitas de umbral. | Funcional · datos sintéticos |
| [Asignación de capital por RAROC](asignacion-de-capital-raroc) | Asignación del presupuesto de crédito entre segmentos maximizando el retorno ajustado por riesgo sujeto a un presupuesto de capital y topes por segmento, resuelto con programación lineal. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
