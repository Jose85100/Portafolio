# Cobertura y brechas de evidencia: ciberseguridad e IA

Corte de revisión: 2026-11-12. Los benchmarks con datos públicos ilustran métodos bajo los supuestos declarados en cada notebook y no prueban desempeño de controles de una entidad.

| Tema | Evidencia disponible | Brecha para la pregunta del proyecto |
|---|---|---|
| [Cambio tecnológico](technology-change/) | Catálogo CISA KEV: diferencias entre fechas de inclusión y vencimiento prescritas. | Inventario de activos afectados y fechas reales de aplicación de parches para medir exposición y eficacia de remediación. |
| [Grafo de ataques](cyber-attack-graphs/) | Mapa descriptivo proveedor-producto a partir de CISA KEV. | Dependencias y trayectorias técnicas verificadas, precondiciones de explotación y controles; el mapa no es un grafo de ataque. |
| [Deriva de modelos IA](ai-model-drift-risk/) | Benchmark Wisconsin Diagnostic: cambio de mezcla construido, PSI, KS y desempeño sobre datos de prueba. | Entradas y predicciones fechadas en producción, etiquetas maduras y decisiones con sus resultados; el benchmark no mide deriva temporal. |
| [Robustez adversarial](adversarial-model-robustness/) | Benchmark Wisconsin Diagnostic: perturbaciones en variables estandarizadas, sensibilidad y ruido aleatorio. | Restricciones de factibilidad del dominio, acceso y capacidad del atacante, etiquetas verificadas tras perturbaciones y evaluación independiente. |
| [Gobierno de IA](ai-governance/) | Diseño S1. | Inventario verificable de modelos, usos, responsables, decisiones de aceptación y hallazgos de revisión; una lista pública de vulnerabilidades no prueba gobierno. |
| [Pérdidas cibernéticas](cyber-loss/) | Diseño S1. | Pérdidas monetarias fechadas, exposición, recuperaciones, cobertura y umbrales de captura; recuentos de CVE no son pérdidas. |
| [Contagio de dependencia tecnológica](technology-dependency-contagion/) | Diseño S1. | Grafo de dependencia real entre proveedores, servicios y clientes, fallos fechados y propagación; nombres de fabricante y producto no acreditan contagio. |

Las fuentes se evaluarán frente al objeto y al grano requeridos. Los datos de diagnóstico médico del benchmark no deben utilizarse para decisiones clínicas.
