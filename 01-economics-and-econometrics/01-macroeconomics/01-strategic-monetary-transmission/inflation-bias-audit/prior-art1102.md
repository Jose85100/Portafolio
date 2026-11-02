# Matriz de fuentes primarias: 2 noviembre2026

Consulta real de documentos oficiales y metadatos/resúmenes editoriales; sin revisión exhaustiva ni prioridad científica. La documentación SciPy recuperada es1.18; ejecución fijada1.17. No depende de una nueva API de kurtosis: K es supuesto externo.

| Referencia verificable | Problema y supuesto | Método/evidencia | Diferencia y límite del proyecto |
|---|---|---|---|
| [MIT18.05 lectura](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/mit18_05_s22_probability.pdf) | Desviaciones con varianza finita | Desigualdad de Chebyshev | Aplicación clásica a media de diferencias cuadradas, no nueva desigualdad |
| [NIST t](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3664.htm) | Student con grados de libertadν | Momentos/kurtosis3(ν−2)/(ν−4) paraν>4 | t5 cumpleK9, no normalidad; t3 no cumple cuarto momento finito |
| [SciPy kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html) | Convenciones de cuarto momento | Pearson versus exceso Fisher | K9 es Pearson y externo; no estimamos K de datos y afirmamos garantía |
| [NIST intervalo](https://www.itl.nist.gov/div898/handbook/prc/section2/prc231.htm) | Intervalo bajo normalidad IID | Pivotechi² | Baseline fuerte más estrecho, falla bajo t5; preservado, no debilitado |
| [Manski2004](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0262.2004.00530.x) | Decisiones con información estadística | Minimax regret en tratamientos | Criterio clásico en otro dominio; no transferimos teoremas a moneda |
| [MIT18.065](https://ocw.mit.edu/courses/18-065-matrix-methods-in-data-analysis-signal-processing-and-machine-learning-spring-2018/resources/lecture-20-definitions-and-inequalities/) | Esperanza, varianza e incertidumbre | Material docente oficial de desigualdades | Complementa fundamento; no evidencia empírica o innovación de nuestro solver |

Aporte defendible: auditoría acumulativa de calibración, amplitud e impacto decisorio de un intervalo bajo cuarto momento acotado. La reducción de supuestos cuesta información y utilidad; el resultado negativo se conserva. referencias.bib contiene14entradas acumuladas y URLs/DOI.
