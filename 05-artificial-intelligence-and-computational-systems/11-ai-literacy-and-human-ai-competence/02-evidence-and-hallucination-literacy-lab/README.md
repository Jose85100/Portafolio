# Evidence & Hallucination Literacy Lab

**Madurez:** S1, especificación. No se declara código ejecutable ni resultados medidos.

## Problema y objetivo

Entrenar y medir capacidad de distinguir evidencia verificable de afirmaciones no sustentadas.

## Modelo formal

Score=Σ_j w_j·1{claim_j supported}; Brier=(1/n)Σ(p_i−y_i)^2.

Definir población objetivo, constructo, unidad de observación, información disponible, variables, supuestos y contraejemplos. Documentar identificabilidad, limitaciones de validez y decisiones derivadas.

## Estadística y experimentación

Estudio aleatorizado de intervención educativa, calibración, Brier, pruebas pareadas. Exigir baseline, intervalos de incertidumbre, diseño sin fuga de información, análisis de sesgos y evaluación fuera de muestra.

## Ingeniería

Python claim extraction/evaluation; corpus con fuentes y fechas; panel de revisión. Arquitectura futura: `contracts/`, `python/`, `tests/`, `experiments/`, `evaluation/`, `reports/`. Reutilizar C++ únicamente si benchmarks justifican su costo.

## Métricas

claim verification F1, calibration, evidence recall. Reportar denominadores, intervalos, segmentación, confiabilidad de anotadores y fallos.

## Gates

G0 pregunta falsable → G1 instrumento/modelo → G2 implementación y tests → G3 evaluación experimental → G4 revisión ética/independiente → G5 despliegue controlado. G2–G5 pendientes.

[Fundamentos](../fundamentals/README.md).
