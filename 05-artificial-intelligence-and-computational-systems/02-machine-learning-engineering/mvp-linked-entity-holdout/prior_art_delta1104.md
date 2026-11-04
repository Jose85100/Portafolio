# Prior art: semántica de deltas bitemporales

| Fuente | Problema/supuestos/método | Evidencia | Diferencia del MVP |
|---|---|---|---|
| Clifford & Isakowitz (1992), [NYU](https://archive.nyu.edu/jspui/handle/2451/14356) | Semántica de transaction, valid y reference time. | Metadata y abstract institucional verificados en el ciclo anterior. | Especializa replay a ledger de vínculos sintético. |
| Jensen & Snodgrass (1996), [DOI](https://doi.org/10.1016/0306-4379(96)00017-8) | Modelo conceptual de información temporal/bitemporal. | DOI/abstract editorial revisados en el ciclo anterior. | No propone un modelo temporal nuevo; mide un error de orden en un gate ML. |
| Torp, Jensen & Snodgrass (2000), [DOI](https://doi.org/10.1007/s007780050008) | Timestamping efectivo en bases temporales. | DOI y página VLDB Journal verificados en ciclo anterior. | No implementa transacciones BD. |
| Kapoor & Narayanan (2023), [DOI](https://doi.org/10.1016/j.patter.2023.100804) | Riesgos de data leakage/reproducibilidad en ML. | Artículo y DOI ya verificados. | Motivación de evaluación temporal; no aporta algoritmo bitemporal. |
| Scikit-learn, [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) | Validación cronológica de muestras ordenadas. | Documentación oficial previamente verificada. | Baseline temporal general, no reconstrucción por arista. |
| Scikit-learn, [data leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | Evitar fuga de datos en preprocesamiento/evaluación. | Documentación oficial previamente verificada. | Este incremento separa vigencia del hecho y disponibilidad del evento. |

Cobertura limitada: fuentes primarias y documentación oficial pertinentes; no es revisión sistemática. Las referencias bibliográficas permanecen en `referencias.bib` del programa.
