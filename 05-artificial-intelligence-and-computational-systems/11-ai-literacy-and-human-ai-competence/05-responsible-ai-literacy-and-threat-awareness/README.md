# Responsible AI Literacy & Threat Awareness Lab

**Madurez:** S1, especificación. No se declara código ejecutable ni resultados medidos.

## Problema y objetivo

Desarrollar evaluación aplicada de privacidad, sesgo, seguridad de prompts, permisos y límites de uso.

## Modelo formal

Risk=Σ_i P(event_i|context,controls)·impact_i; cobertura de políticas.

Definir población objetivo, constructo, unidad de observación, información disponible, variables, supuestos y contraejemplos. Documentar identificabilidad, limitaciones de validez y decisiones derivadas.

## Estadística y experimentación

Experimentos por escenarios, consistencia de juicios, false accept/false reject, sensibilidad por perfiles. Exigir baseline, intervalos de incertidumbre, diseño sin fuga de información, análisis de sesgos y evaluación fuera de muestra.

## Ingeniería

Python simulador de escenarios defensivos; reglas versionadas; SQL auditoría. Arquitectura futura: `contracts/`, `python/`, `tests/`, `experiments/`, `evaluation/`, `reports/`. Reutilizar C++ únicamente si benchmarks justifican su costo.

## Métricas

unsafe action rate, policy recall, false blocks, privacy awareness. Reportar denominadores, intervalos, segmentación, confiabilidad de anotadores y fallos.

## Gates

G0 pregunta falsable → G1 instrumento/modelo → G2 implementación y tests → G3 evaluación experimental → G4 revisión ética/independiente → G5 despliegue controlado. G2–G5 pendientes.

[Fundamentos](../fundamentals/README.md).
