# Evidence-Grounded Research Agents

> **Estado: propuesta técnica (S0/S1).** No se declara implementación, benchmark ejecutado ni desempeño demostrado.

## Pregunta de investigación

¿Puede un sistema de agentes con revisión adversarial reducir afirmaciones económicas no sustentadas?

## Hipótesis y mecanismo

Formalizar una hipótesis falsable con variables observables, supuestos, población objetivo y al menos una explicación alternativa. Separar claramente innovación metodológica de adaptación aplicada.

## Modelo y algoritmos

Planner-retriever-critic con roles y trazabilidad de evidencia, evaluación por adjudicación independiente.

Especificar función objetivo, restricciones, estimador/algoritmo, complejidad temporal y espacial, condiciones de convergencia o contraejemplos; registrar las dependencias y semillas.

## Datos, experimentos y validación

Benchmark de afirmaciones y documentos públicos; precisión de citas, cobertura, costo y tasa de alucinación.

Requisitos: dataset público con licencia, corte temporal point-in-time, baseline simple y avanzado, ablaciones, intervalos de incertidumbre, pruebas de fuga de información, sensibilidad y evaluación fuera de muestra. No afirmar causalidad sin diseño identificable.

## Entregables por madurez

1. S1: literatura contrastada, especificación formal y protocolo reproducible.
2. S2: implementación mínima, pruebas unitarias y dataset de ejemplo.
3. S3: benchmarks, robustez, reproducibilidad y evaluación de fallos.
4. S4: documentación de riesgos, auditoría independiente y demostración reproducible.

## Límites

La validez externa, los cambios de distribución, los costes computacionales y la gobernanza de datos requieren verificación empírica; ningún resultado está establecido aún.
