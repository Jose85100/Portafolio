# Matriz primaria — 1 noviembre 2026

Metadatos/resúmenes y fórmulas de documentación primaria consultados el1nov2026 por búsqueda/apertura web. No revisión exhaustiva ni acceso completo a todos artículos. Se conservan6fuentes anteriores y añaden4; BibTeX10entradas. Cinco fuentes pertinentes mínimas no equivalen a evidencia de originalidad.

| Fuente verificable | Problema/supuestos/método | Evidencia/diferencia concreta |
|---|---|---|
| [NIST7.2.3.1](https://www.itl.nist.gov/div898/handbook/prc/section2/prc231.htm) | Intervalo de desviación estándar mediante chi², normalidad | Reproducimos fórmula al cuadrado, la conectamos al solver31 y auditamos ruptura; no inventamos intervalo |
| [SciPychi²1.17](https://cache-docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.chi2.html) | PPF y distribución gamma equivalente | API comprobada; testindependiente scipy.special.gammaincinv; misma biblioteca subyacente, no independencia total de software |
| [SciPyt1.17](https://cache-docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.t.html) | Distribución de Student con escala/grados libertad | Adverso t5 con varianza igual, no ley exacta pivotal; control de especificación |
| [Wilson1927DOI](https://www.tandfonline.com/doi/abs/10.1080/01621459.1927.10502953) | Inferencia de proporciones | Barras Wilson95% para indicadores MC, no confundidas con intervalo90% de v; metadatos verificados, fórmula score clásica implementada |
| [Rogoff1985](https://academic.oup.com/qje/article-abstract/100/4/1169/1895960) | Tradeoff delegación conservadora | Motor LQ clásico conservado, nueva restricción informativa no implica novedad de teoría |
| [Manski2004DOI](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0262.2004.00530.x) | Decisiones minimaxregret con datos experimentales | Criterio conocido; distinto dominio monetario, sin transferir teoremas de tratamiento |

Clasificación: auditoría/adaptación de ingeniería acumulativa. Aporte defendible al repositorio: límite condicional de decisión separado de calibración y de ganancia media, con contraejemplo temporal reproducible. Resultado disciplinar original no establecido.
