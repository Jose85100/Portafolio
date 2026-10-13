# Prompt & Task Specification Engineering Lab

**Madurez:** S1, especificación. No se declara código ejecutable ni resultados medidos.

## Problema y objetivo

Convertir necesidades ambiguas en especificaciones de tareas, contratos, pruebas y criterios de aceptación.

## Modelo formal

argmin_s E[task_loss(s)]+λ·complexity(s) sujeto a constraints(s).

Definir población objetivo, constructo, unidad de observación, información disponible, variables, supuestos y contraejemplos. Documentar identificabilidad, limitaciones de validez y decisiones derivadas.

## Estadística y experimentación

A/B de especificaciones, evaluación ciega, consistencia entre evaluadores y control de dificultad. Exigir baseline, intervalos de incertidumbre, diseño sin fuga de información, análisis de sesgos y evaluación fuera de muestra.

## Ingeniería

Python task harness, JSON Schema, tests y evaluación automática/humana. Arquitectura futura: `contracts/`, `python/`, `tests/`, `experiments/`, `evaluation/`, `reports/`. Reutilizar C++ únicamente si benchmarks justifican su costo.

## Métricas

task success, specification coverage, rework rate. Reportar denominadores, intervalos, segmentación, confiabilidad de anotadores y fallos.

## Gates

G0 pregunta falsable → G1 instrumento/modelo → G2 implementación y tests → G3 evaluación experimental → G4 revisión ética/independiente → G5 despliegue controlado. G2–G5 pendientes.

[Fundamentos](../fundamentals/README.md).
