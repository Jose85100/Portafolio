# Computational Economics — infraestructura transversal

**Estado: arquitectura propuesta.** Compartida por macroeconomía, microeconomía, teoría de juegos, econometría y macrofinanzas.

| Módulo | Objetivo | Criterios de validación |
|---|---|---|
| `bayesian-games/` | Estrategias y posterior bajo información incompleta | Bayes consistency, best responses, convergence |
| `stochastic-games/` | Equilibrios de Markov y programación dinámica | Bellman residual, policy improvement |
| `mean-field-games/` | Acoplamiento población-individuo | Fixed-point residual, mass conservation |
| `mechanism-design/` | Contratos IC/IR y bienestar | Feasibility, IC/IR, welfare gap |
| `equilibrium-solvers/` | Best response, continuation y complementarity | Residuals, sensitivity, multiple starts |
| `structural-estimation/` | SMM, indirect inference y likelihood | Identification, simulation error, coverage |
| `numerical-validation/` | Monte Carlo, bootstrap, stability, benchmarks | Reproducibility, numerical convergence |

No hay solvers implementados en este directorio. Cada módulo futuro deberá incluir API, tests, benchmark, documentación y casos degenerados.
