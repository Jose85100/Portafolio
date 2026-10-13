# bayesian-games

**Estado:** laboratorio computacional inicial; no es un solver completo.

## Problema
Actualización de creencias y decisiones bayesianas.

## Especificación de implementación
- API de entrada tipada, estados y acciones explícitos, tolerancias y semilla.
- Residuo matemático y condiciones de factibilidad; informar no convergencia.
- Baseline numérico verificable, tests de casos degenerados y estudio de sensibilidad.
- Motor transversal disponible: [econlab.py](../src/econlab.py). El motor actual solo ofrece utilidades OLS, bootstrap, pérdidas esperadas, Markov y best response de grilla.

## Validación futura
Comparar con soluciones analíticas cuando existan, evaluar convergencia en refinamiento de grilla y estabilidad de resultados.

## Prototipo disponible

[Bayesian Freeze Audit](../../03-game-theory/01-endogenous-credit-freeze/bayesian-freeze-audit/) implementa un caso finito de dos agentes y dos tipos, con oracle racional y regret. No es un solver bayesiano genérico ni continuo.
