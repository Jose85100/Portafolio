# structural-estimation

**Estado:** laboratorio computacional inicial; no es un solver completo.

## Problema
Estimación por momentos simulados e identificación.

## Especificación de implementación
- API de entrada tipada, estados y acciones explícitos, tolerancias y semilla.
- Residuo matemático y condiciones de factibilidad; informar no convergencia.
- Baseline numérico verificable, tests de casos degenerados y estudio de sensibilidad.
- Motor transversal disponible: [econlab.py](../src/econlab.py). El motor actual solo ofrece utilidades OLS, bootstrap, pérdidas esperadas, Markov y best response de grilla.

## Validación futura
Comparar con soluciones analíticas cuando existan, evaluar convergencia en refinamiento de grilla y estabilidad de resultados.
