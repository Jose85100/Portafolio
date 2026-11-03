# Matriz de prior art — historial point-in-time de adjudicación

Fuentes consultadas/verificadas en sus páginas primarias el 3-nov-2026. La comparación es de alcance conceptual, no una revisión sistemática exhaustiva.

| Fuente primaria | Problema / supuestos / método | Evidencia | Diferencia concreta del incremento |
|---|---|---|---|
| Clifford & Isakowitz (1992), [NYU IS-92-42](https://archive.nyu.edu/jspui/handle/2451/14356) | Semántica formal de transaction time, valid time y reference time. | Working paper de 40p; metadata y resumen institucional verificados; no prueba específica de ML. | Este MVP especializa el orden de consulta a historial de adjudicaciones con full replacement; no reclama bitemporalidad nueva. |
| Jensen & Snodgrass (1996), [Semantics of Time-Varying Information](https://doi.org/10.1016/0306-4379(96)00017-8) | Modelo conceptual y semántica de datos temporales/bitemporales. | DOI y resumen editorial verificados. | Base teórica para separar tiempo del hecho y tiempo de registro; el repo añade contraejemplo ejecutable de filter-first. |
| Torp, Jensen & Snodgrass (2000), [Effective Timestamping in Databases](https://doi.org/10.1007/s007780050008) | Captura de valid y transaction timestamps y modificaciones consistentes en BD. | Registro institucional de autores y página de VLDB Journal verificados; DOI corregido tras cotejar el registro. | No se implementa una BD ni su transacción; solo un selector reproducible para el contrato local de revisiones completas. |
| Kapoor & Narayanan (2023), [Leakage and the Reproducibility Crisis](https://doi.org/10.1016/j.patter.2023.100804) | Taxonomía/análisis de fuga en ML científico, incluida fuga temporal. | Artículo y DOI verificados; relevante para motivación de evaluación, no para semantic identity histories. | Este MVP no mide inflación predictiva; aísla un mecanismo de temporalidad previo al modelado. |
| Scikit-learn, [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) | Cortes cronológicos para evaluación temporal; datos ordenados y observaciones. | Documentación oficial verificada. | Aporta baseline de evaluación temporal a nivel muestra, pero no selecciona revisiones bitemporales de una entidad. |
| Scikit-learn, [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html) | Evitar uso de información de test/tiempo futuro en transformaciones y evaluación. | Documentación oficial verificada. | Relevancia de leakage general; nuestra comparación distingue disponibilidad del registro de la vigencia del hecho. |

## Tres candidatos

1. latest-available → interval-valid (elegido: pequeño, extiende el snapshot gate, produce caso refutable).
2. normalizar base a intervalos no solapados con consultas bitemporales (más general, pero necesita migrar contratos almacenamiento).
3. autenticar procedencia y disponibilidad mediante firma (no implementable sin emisor/PKI/contrato).

Clasificación del aporte: adaptación de ingeniería y auditoría adversarial; evidencia limitada a fixtures sintéticas diseñadas. Sin afirmación de novedad científica u originalidad mundial.
