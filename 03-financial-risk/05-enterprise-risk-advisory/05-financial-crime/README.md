# Fraude, AML y cumplimiento — bases + 7 proyectos

**Bases especializadas:** [fundamentals/](fundamentals/) · **Bases transversales:** [00-foundations/](../00-foundations/)

Los fundamentos son independientes del catálogo; **no cuentan** entre los siete proyectos.

Se mantienen los tres proyectos existentes y se incorporan cuatro líneas nuevas. Todos deben adoptar los [contratos y criterios transversales](../00-architecture/README.md) sin sustituir su matemática especializada.

## Catálogo

- **Existente:** [Fraude y redes de colusión](fraud-graphs/)
- **Existente:** [AML/CFT basado en riesgo](aml-typologies/)
- **Existente:** [Obligaciones regulatorias y control testing](regulatory-controls/)
- **Nuevo S1:** [Detección temporal de redes de fraude](fraud-dynamic-networks/)
- **Nuevo S1:** [Priorización de alertas AML](aml-alert-prioritization/)
- **Nuevo S1:** [Evaluación causal de medidas antifraude](fraud-causal-intervention/)
- **Nuevo S1:** [Impacto de cambios regulatorios](regulatory-change-impact/)

## Cobertura de aplicaciones y datos pendientes

| Tema | Evidencia disponible y alcance |
|---|---|
| [Tipologías AML](aml-typologies/) | Composición descriptiva de sanciones OFAC; no identifica tipologías de lavado ni delitos. |
| [Controles regulatorios](regulatory-controls/) | Completitud descriptiva de un corte OFAC; no verifica efectividad del screening. |
| [Priorización de alertas](aml-alert-prioritization/) | Comparación histórica de dos reglas geográficas con sujetos reportados en SAR FinCEN; no evalúa alertas individuales ni precisión. |
| [Fraude causal e intervención](fraud-causal-intervention/) | **Pendiente:** asignación de intervenciones, fechas, resultados y datos de selección; no se identifica causalidad con volúmenes SAR. |
| [Redes dinámicas de fraude](fraud-dynamic-networks/) | **Pendiente:** relaciones entre entidades, fecha de cada arista, cobertura y etiquetas de fraude; un conteo por estado no es un grafo. |
| [Grafos de fraude](fraud-graphs/) | **Pendiente:** transacciones o vínculos desidentificados con estructura y etiquetas verificables; no se infiere fraude de pertenencia a listas. |
| [Impacto de cambios regulatorios](regulatory-change-impact/) | **Pendiente:** versiones normativas fechadas, ámbito y evidencia de implementación o resultados; no inferir efecto causal de una cronología. |

Las tres aplicaciones actuales proporcionan contexto o diagnósticos acotados, no validación de un sistema institucional de prevención de crimen financiero.
