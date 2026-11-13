# Liderazgo de datos

Gobierno de datos, arquitectura analítica y organización de equipos y fuentes de datos.

## Proyectos

| Proyecto | Qué hace | Estado |
|---|---|---|
| [Reglas de calidad de datos](reglas-de-calidad-de-datos) | Marco de reglas de calidad de datos sobre una tabla de clientes con problemas inyectados: completitud, unicidad, rangos válidos, integridad referencial y actualidad. | Funcional · datos sintéticos |
| [Manifiesto de datos con SHA-256](manifiesto-de-datos-sha256) | Laboratorio controlado y verificación reproducible de integridad/esquema sobre un extracto oficial mensual del IPC de DANE. | Laboratorio + aplicación observada |
| [Detección de drift de datos con PSI y KS](deteccion-de-drift-psi-ks) | Laboratorio sintético más comparación observada del cambio de distribución de inflación mensual IPC entre ventanas; sin claim de drift de modelo. | Laboratorio + aplicación observada |
| [Linaje de datos y análisis de impacto](linaje-e-impacto-de-datos) | Catálogo mínimo de conjuntos de datos con sus dependencias. | Funcional · datos sintéticos |
| [Priorización de casos de uso de datos](priorizacion-de-casos-de-uso) | Matriz de priorización de iniciativas de datos con puntaje ponderado de valor (beneficio, ajuste estratégico) y esfuerzo (costo, riesgo, preparación de datos), clasificación en cuadrantes y análisis de sensibilidad a los pesos. | Funcional · datos sintéticos |

Cada proyecto trae su `main.py` ejecutable y el resultado de una corrida reproducible. Las aplicaciones observadas se documentan por separado y no certifican la calidad integral de la fuente ni validan controles institucionales.
