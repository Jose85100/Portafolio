# Human–AI Decision Calibration Lab

**Madurez:** S1, especificación. No se declara código ejecutable ni resultados medidos.

## Problema y objetivo

Evaluar cuándo una persona debe aceptar, revisar o rechazar una recomendación automatizada.

## Modelo formal

a*=argmin_{a∈{accept,review,reject}} E[L(a,Y)|x,p_model].

Definir población objetivo, constructo, unidad de observación, información disponible, variables, supuestos y contraejemplos. Documentar identificabilidad, limitaciones de validez y decisiones derivadas.

## Estadística y experimentación

Experimentos de decisiones con y sin IA, sobreconfianza, sesgo de automatización y heterogeneidad. Exigir baseline, intervalos de incertidumbre, diseño sin fuga de información, análisis de sesgos y evaluación fuera de muestra.

## Ingeniería

Python experiment runner; SQL eventos; dashboards. Arquitectura futura: `contracts/`, `python/`, `tests/`, `experiments/`, `evaluation/`, `reports/`. Reutilizar C++ únicamente si benchmarks justifican su costo.

## Métricas

decision accuracy, selective risk, calibration, override quality. Reportar denominadores, intervalos, segmentación, confiabilidad de anotadores y fallos.

## Gates

G0 pregunta falsable → G1 instrumento/modelo → G2 implementación y tests → G3 evaluación experimental → G4 revisión ética/independiente → G5 despliegue controlado. G2–G5 pendientes.

[Fundamentos](../fundamentals/README.md).
