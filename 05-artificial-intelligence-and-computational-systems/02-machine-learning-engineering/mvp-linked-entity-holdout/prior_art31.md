# Matriz de fuentes primarias verificadas el31 de octubre de2026

Las cinco páginas se abrieron realmente mediante búsqueda web. El DOI directo devolvió403; se verificó el texto completo del artículo en PMC. No revisión sistemática exhaustiva de entity resolution. No novedad mundial. Claves BibTeX audit31*.

|Referencia|Problema y supuestos|Método/evidencia existente|Diferencia local y límite|
|---|---|---|---|
|Kapoor y Narayanan2023, DOI10.1016/j.patter.2023.100804, PMC10499856|Fuga y reproducibilidad en ciencia ML|Taxonomía, revisión y estudio de reproducción|Motiva auditoría; este proyecto solo prueba particiones sintéticas y no reproduce su estudio empírico|
|sklearn GroupShuffleSplit|Grupos dados, partición por grupos|Documentación de unidad de test_size y ausencia de grupos compartidos|Baseline count30 usa SHA256 y no afirma reproducir la aleatoriedad sklearn; no certifica calidad del grupo suministrado|
|sklearn pair_confusion_matrix|Dos particiones sobre igual universo|Contingencia entre pares ordenados coasignados/no coasignados|Implementación independiente con enteros y pares NO ordenados, mitad de conteos sklearn; auditoría adicional de filas expuestas|
|NetworkX connected_components|Grafo no dirigido explícito|Cierre transitivo conocido, BFS|Reúso splitter29; no inventa algoritmo ni infiere vínculos; documentación no garantiza que el grafo sea verdadero|
|sklearn precision_recall_fscore_support|Verdad de etiquetas y predicciones suministradas|Métricas derivadas de TP/FP/FN y tratamiento de divisiones nulas|Se conservan conteos enteros sin normalizar para evitar precisión/recall indefinidos con0 pares; no nuevo estimador|

Aporte respecto al repositorio:30 probaba garantía sobre el MISMO grafo;31 admite un segundo snapshot adjudicado y demuestra cuándo falla la lectura fuerte de esa garantía. Clasificación **auditoría y adaptación de ingeniería**. Frente a literatura se integran conceptos conocidos en una herramienta local; no se acredita extensión metodológica original. Contraste justo: count30 y DP30 reciben idéntico snapshot observado; el oráculo adjudicado tiene información privilegiada declarada.
