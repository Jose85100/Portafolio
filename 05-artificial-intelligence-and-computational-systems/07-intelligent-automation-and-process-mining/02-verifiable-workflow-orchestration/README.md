# Verifiable Workflow Orchestration

> **Estado: prototipo algorítmico inicial (S2 parcial).** `src/model.py` contiene un baseline ejecutable y `tests/test_model.py` comprueba comportamiento esencial. No existe todavía validación empírica completa.

## Pregunta de investigación

¿Cómo garantizar idempotencia, reconciliación y evidencia en automatizaciones financieras?

## Hipótesis y mecanismo

Formalizar una hipótesis falsable con variables observables, supuestos, población objetivo y al menos una explicación alternativa. Separar claramente innovación metodológica de adaptación aplicada.

## Modelo y algoritmos

Máquinas de estado, saga/compensaciones, contratos de datos y observabilidad.

Especificar función objetivo, restricciones, estimador/algoritmo, complejidad temporal y espacial, condiciones de convergencia o contraejemplos; registrar las dependencias y semillas.

## Datos, experimentos y validación

Simulación de fallos, duplicados y reintentos; tasa de inconsistencias y recovery time.

Requisitos: dataset público con licencia, corte temporal point-in-time, baseline simple y avanzado, ablaciones, intervalos de incertidumbre, pruebas de fuga de información, sensibilidad y evaluación fuera de muestra. No afirmar causalidad sin diseño identificable.

## Código y reproducción

- [Implementación inicial](src/model.py) y [prueba unitaria](tests/test_model.py).
- Desde la raíz del repositorio:

```bash
python -m unittest discover -s 05-artificial-intelligence-and-computational-systems/07-intelligent-automation-and-process-mining/02-verifiable-workflow-orchestration/tests -p test_model.py -v
```

**Alcance:** el baseline no equivale a la implementación completa de los métodos avanzados propuestos ni demuestra desempeño en datos reales.

## Entregables por madurez

1. S1: literatura contrastada, especificación formal y protocolo reproducible.
2. S2: implementación mínima, pruebas unitarias y dataset de ejemplo.
3. S3: benchmarks, robustez, reproducibilidad y evaluación de fallos.
4. S4: documentación de riesgos, auditoría independiente y demostración reproducible.

## Límites

La validez externa, los cambios de distribución, los costes computacionales y la gobernanza de datos requieren verificación empírica; no hay resultados de desempeño empírico ni validación operativa establecidos.
