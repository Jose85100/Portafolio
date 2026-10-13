# AI Competency Assessment Engine

**Madurez:** S1, especificación. No se declara código ejecutable ni resultados medidos.

## Problema y objetivo

Medir habilidades de comprensión, formulación, evaluación y supervisión de IA mediante instrumentos psicométricos.

## Modelo formal

P(Y_ij=1|θ_i)=σ(a_j(θ_i−b_j)); θ_i competencia latente.

Definir población objetivo, constructo, unidad de observación, información disponible, variables, supuestos y contraejemplos. Documentar identificabilidad, limitaciones de validez y decisiones derivadas.

## Estadística y experimentación

IRT 2PL, validez de constructo, funcionamiento diferencial de ítems, fiabilidad y calibración. Exigir baseline, intervalos de incertidumbre, diseño sin fuga de información, análisis de sesgos y evaluación fuera de muestra.

## Ingeniería

Python estimación IRT; SQL respuestas anonimizadas; API de evaluación. Arquitectura futura: `contracts/`, `python/`, `tests/`, `experiments/`, `evaluation/`, `reports/`. Reutilizar C++ únicamente si benchmarks justifican su costo.

## Métricas

calibration, reliability, DIF, test information. Reportar denominadores, intervalos, segmentación, confiabilidad de anotadores y fallos.

## Gates

G0 pregunta falsable → G1 instrumento/modelo → G2 implementación y tests → G3 evaluación experimental → G4 revisión ética/independiente → G5 despliegue controlado. G2–G5 pendientes.

[Fundamentos](../fundamentals/README.md).
