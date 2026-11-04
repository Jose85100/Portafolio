# Matriz de antecedentes (consulta 2026-11-04)

| Fuente | Problema/método/supuesto | Evidencia | Diferencia concreta |
|---|---|---|---|
| Raiffa & Schlaifer (1961), *Applied Statistical Decision Theory*, [catálogo](https://books.google.com/books?id=KxQ9AAAAYAAJ) | Decisiones bayesianas bajo incertidumbre; utilidad especificada | Texto fundacional; no evaluado empíricamente aquí | Nuestro MVP particulariza el cálculo a menú de 2 precios y piloto finito |
| Lindley (1956), [DOI](https://doi.org/10.1093/biomet/44.1-2.187) | Medida de información de un experimento, marco bayesiano | Desarrollo teórico | Se usa diferencia de valor óptimo de decisión, no entropía como sustituto |
| Wilson et al. (2022), [DOI](https://doi.org/10.1177/0272989X211026292) | Simular datos de estudio para EVSI; requiere modelo de datos | Tutorial/aplicación metodológica | Contraste exacto Beta-Binomial de juguete, sin Monte Carlo ni decisión clínica |
| Heath et al. (2020), [White Rose](https://eprints.whiterose.ac.uk/id/eprint/163335/) | Métodos eficientes de estimación EVSI en modelos costosos | Comparación de cuatro estimadores | Problema aquí es pequeño y cerrado, por eso suma exacta |
| *A Closed-Form EVSI Expression...* (2023), [DOI](https://doi.org/10.1287/deca.2022.0462) | Expresión cerrada para multinomial acotado y tamaño óptimo | Resultado analítico | Nuestro caso independiente de dos brazos Bernoulli, enumerate outcomes |
| Strong et al. (2015), [DOI](https://doi.org/10.1177/0272989X15575286) | Estimación EVSI por regresión sobre muestras de sensibilidad probabilística | Método no paramétrico | MVP usa conjugación y enumera toda predictiva; no compite en escalabilidad |

Cobertura: revisados abstract/resumen y metadatos de las fuentes web citadas; no lectura integral de todos los artículos. Fuentes sostienen concepto y baseline, no novedad original.
