# Riesgo de crédito: productos

Scoring, originación y seguimiento de productos de crédito: PD/LGD/EAD, segmentación y desempeño de carteras por producto.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Scorecard logístico con WoE e IV](scorecard-logistico-woe) | Construcción de un scorecard de probabilidad de incumplimiento: discretización por cuantiles, Weight of Evidence, Information Value, regresión logística y evaluación con AUC y KS en una muestra de prueba. | Funcional · datos sintéticos |
| [Pérdida esperada por producto (PD, LGD, EAD)](perdida-esperada-pd-lgd-ead) | Cálculo de la pérdida esperada EL = PD x LGD x EAD a nivel de crédito para cuatro productos, con distribuciones beta para PD y LGD, y verificación por simulación Monte Carlo de incumplimientos. | Funcional · datos sintéticos |
| [Matrices de transición y roll rates](matrices-de-transicion-roll-rates) | Estimación por máxima verosimilitud de una matriz de transición entre estados de mora (al día, 30, 60, 90+ días y default absorbente) a partir de historias simuladas, y cálculo de la PD acumulada a 12 meses con potencias de la matriz. | Funcional · datos sintéticos |
| [Análisis de cosechas (vintage)](analisis-de-cosechas-vintage) | Curvas de incumplimiento acumulado por cohorte de originación con una hazard que crece y decae con la antigüedad. | Funcional · datos sintéticos |
| [Segmentación de clientes con k-means](segmentacion-clientes-kmeans) | Segmentación de clientes por comportamiento de crédito con k-means: estandarización, elección de k por coeficiente de silueta y lectura de la tasa de incumplimiento y el perfil de cada segmento. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
