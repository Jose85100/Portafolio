# Cobertura y brechas de evidencia: resiliencia operacional

Corte de revisión: 2026-11-12. Una fuente de contexto se identifica por la pregunta que permite responder; no se cuenta como validación de un modelo de pérdida o recuperación.

| Tema | Evidencia disponible | Brecha para la pregunta del proyecto |
|---|---|---|
| [Continuidad](business-continuity/) | Notebook con reportes agregados UNGRD por categoría. | Fechas de interrupción y recuperación, servicios y dependencias, exposición y resultados de pruebas de continuidad por entidad. |
| [Pérdidas operativas](loss-distribution/) | Notebook con accidentalidad laboral sectorial y escenarios Poisson supuestos. | Incidentes operacionales con fecha, exposición, severidad monetaria, recuperaciones y umbral de reporte para estimar frecuencia y severidad. |
| [Recuperación estocástica](recovery-time-stochastic/) | Benchmark VCDB con tiempos observados hasta contención de incidentes públicos; descarga y hash fijados. | Registro completo de restauración, inicio, cierre y estado de censura por incidente; contención no equivale a recuperación. |
| [Efectividad causal de controles](control-effectiveness-causal/) | Diseño S1. | Intervención y fecha de implantación por unidad, grupo comparable, exposición, calendario de medición y resultados para contrastar supuestos de identificación. |
| [Cola extrema operacional](operational-extreme-tail/) | Diseño S1. | Pérdidas monetarias positivas con umbral de registro, recuperación y exposición; un recuento de incidentes no identifica la severidad ni su cola. |
| [Redes de resiliencia](resilience-network-percolation/) | Diseño S1. | Nodos y dependencias observadas de procesos, umbrales de interrupción y tiempos de recuperación; un grafo de proveedores-productos no demuestra dependencia operativa. |
| [Riesgo de terceros](third-party/) | Diseño S1. | Contratos y proveedores, servicios consumidos, dependencias compartidas, incidentes y duración; los nombres de proveedores de un catálogo de vulnerabilidades no son inventario de contratos. |

La disponibilidad de una fuente pública adecuada requiere búsqueda y evaluación adicional. No se reemplazan estas brechas con escenarios construidos que carezcan de etiquetas relevantes.
