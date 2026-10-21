# Computational Economics — infraestructura transversal

**Estado: arquitectura propuesta con componentes S2 parciales.** Compartida por macroeconomía, microeconomía, teoría de juegos, econometría y macrofinanzas.

| Módulo | Objetivo | Criterios de validación |
|---|---|---|
| `bayesian-games/` | Estrategias y posterior bajo información incompleta | Bayes consistency, best responses, convergence |
| `stochastic-games/` | Equilibrios de Markov y programación dinámica | Bellman residual, policy improvement |
| `mean-field-games/` | Acoplamiento población-individuo | Fixed-point residual, mass conservation |
| `mechanism-design/` | Contratos IC/IR y bienestar | Feasibility, IC/IR, welfare gap |
| `equilibrium-solvers/` | Best response, continuation y complementarity | Residuals, sensitivity, multiple starts |
| `structural-estimation/` | SMM, indirect inference y likelihood | Identification, simulation error, coverage |
| `numerical-validation/` | Monte Carlo, bootstrap, stability, benchmarks | Reproducibility, numerical convergence |

Existe un núcleo estadístico sintético con OLS, bootstrap, ECL, paso Markov y best response en grilla; no son solvers estructurales completos. Cada módulo futuro deberá incluir API, tests, benchmark, documentación y casos degenerados.

El componente `numerical-validation/quadratic-root-certificate/` (2026-10-21) aporta envolventes racionales reproducibles para raíces cuadráticas de regímenes; no convierte la infraestructura completa en S3 ni certifica equilibrios multivariados.
