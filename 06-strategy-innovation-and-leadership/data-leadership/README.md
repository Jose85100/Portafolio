# Liderazgo de datos

Gobierno de datos, arquitectura analítica y organización de equipos y fuentes de datos.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Reglas de calidad de datos](reglas-de-calidad-de-datos) | Marco de reglas de calidad de datos sobre una tabla de clientes con problemas inyectados: completitud, unicidad, rangos válidos, integridad referencial y actualidad. | Funcional · datos sintéticos |
| [Manifiesto de datos con SHA-256](manifiesto-de-datos-sha256) | Construcción de un manifiesto con hash SHA-256, tamaño y número de filas por archivo, y verificación de integridad posterior. | Funcional · datos sintéticos |
| [Detección de drift de datos con PSI y KS](deteccion-de-drift-psi-ks) | Monitoreo de cambios de distribución entre un período de referencia y uno actual: PSI y prueba de Kolmogorov-Smirnov por variable, con niveles de alerta y un resumen de variables a revisar. | Funcional · datos sintéticos |
| [Linaje de datos y análisis de impacto](linaje-e-impacto-de-datos) | Catálogo mínimo de conjuntos de datos con sus dependencias. | Funcional · datos sintéticos |
| [Priorización de casos de uso de datos](priorizacion-de-casos-de-uso) | Matriz de priorización de iniciativas de datos con puntaje ponderado de valor (beneficio, ajuste estratégico) y esfuerzo (costo, riesgo, preparación de datos), clasificación en cuadrantes y análisis de sensibilidad a los pesos. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida real. Las versiones con datos reales abiertos se agregarán por separado.
