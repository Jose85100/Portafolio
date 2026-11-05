# Extensión exploratoria: shocks comunes por estado del oponente

## Tres candidatas

1. Errores de pago correlacionados entre acciones propias pero específicos al estado del oponente (seleccionada: tiene una implicación exacta y prueba por vértices pequeña).
2. Incertidumbre del prior de señales (pospuesta: requiere extender el juego bayesiano y fijar el estimando).
3. Expansión a más de dos acciones (pospuesta: requiere nuevo oráculo y más alcance de implementación).

## Pregunta e hipótesis

¿Cambian el regret y la recomendación si el error de payoff es un shock común a las acciones propias, condicionado a la acción del oponente? Hipótesis refutable: con `u_ij(θ)=A_ij+θ_j`, `|θ_j|≤δ`, el regret en cualquier mezcla coincide exactamente con el regret nominal para todo vértice del conjunto de shocks.

## Derivación

Para desviación pura `a` contra mezcla propia `p` y rival `q`, el cambio de utilidad es
`Σ_j q_j[(A_aj+θ_j)−Σ_i p_i(A_ij+θ_j)]`.
El término de shock es `Σ_j q_j θ_j(1−Σ_i p_i)=0`, ya que `Σ_i p_i=1`. Por tanto la cota sharp es el regret nominal, independiente de `δ`. Se conserva el ranking bajo este conjunto estructurado; esto no es cierto para errores independientes por celda, cuyo soporte puede ser positivo.

## Estado

Código en `src/uncertainty_structures.py`; pruebas focales incluyen los cuatro vértices y entradas no finitas. Datos/ejemplo sintéticos. Aporte: adaptación de ingeniería y resultado de cancelación verificable, no una contribución científica original. `informe_structured.md` registra la ablación negativa y límites; el nivel S del programa depende de revisión independiente y alcance del estándar.
