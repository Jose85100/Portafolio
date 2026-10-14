# Registro de revisión dirigida — 2026-10-14

Consultas reales: Bayesian mixed equilibrium; support enumeration; Harsanyi
incomplete information; Lemke Howson; coordinación/global games. Se buscaron
también resultados con dominios de arXiv, SSRN, NBER, CEPR, Semantic Scholar y
Papers with Code. No revisión sistemática ni verificación de prioridad.

| Fuente | Cobertura y resultado |
|---|---|
| INFORMS | Harsanyi 1967, DOI y página editorial abiertos. |
| SIAM | Lemke/Howson 1964, DOI y página editorial abiertos. También se localizó Enumeration of All Extreme Equilibria, sin usar sus resultados como si se replicaran. |
| Gambit | Documentación oficial v16.4.0 abierta: soportes, regret y singularidad; un soporte singular no implica por sí solo familia factible. Gambit no se instaló ni se benchmarkeó. |
| NBER | w22297 localizado por búsqueda con DOI; referencia contextual, no lectura completa nueva. |
| CEPR | DP12392/DP4995/DP16484 localizados; coordinación en redes y juegos globales. Referencia Rochet/Vives de la bibliografía anterior conservada. |
| SSRN | 2265131, 478982 y otros resultados de estrategias mixtas/complementariedad localizados; texto completo no verificado en este ciclo. |
| arXiv | Consultas de Bayesian/mixed/support y categorías econ.EM/econ.TH/q-fin.EC/math.OC/stat.ME. Resultados generales de juegos bayesianos; no antecedente específico de este artefacto validado. La cobertura por categoría es insuficiente. |
| Semantic Scholar | Consultas restringidas por dominio sin resultados propios utilizables; no se consultó exhaustivamente su API. |
| Papers with Code | Material de Nash/mixed/learning localizado; sin benchmark directamente comparable al juego crediticio. |
| Econometrica/AER/JPE/JET/GEB | Contexto del ciclo previo; aquí se localizaron trabajos de coordinación y pruebas experimentales, sin revisión exhaustiva de esas revistas. |
| QJE/ReStud/Journal of Econometrics | No artículos específicos verificados en este ciclo; cobertura pendiente, no ausencia de antecedentes. |

La novedad es de integración y validación incremental: extender un baseline puro
existente con soporte mixto, comparar contra aritmética racional y fallar de forma
explícita cuando no puede certificarse una lista aislada. No es un algoritmo nuevo
de equilibrio ni una refutación de teoremas de juegos globales.
