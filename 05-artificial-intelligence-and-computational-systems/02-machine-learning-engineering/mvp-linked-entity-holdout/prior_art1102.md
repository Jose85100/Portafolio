# Selección y prior art —2 de noviembre de2026

## Tres ideas candidatas

|Idea|Brecha/relevancia|Diferencia respecto al programa|Valor de herramienta|Viabilidad|Evidencia necesaria/decisión|
|---|---|---|---|---|---|
|Contrato temporal y semántico|1101 requiere equivalencia completa, pero el llamador podía suministrar enlaces positivos/fechas futuras|Gate local previo a cotas, manifiesto canónico|Bloquea declaraciones inadmisibles con motivos sin inventar cotas|Alta, fixtures/timestamps y oráculo de reglas|Comparación as-of, límites de confianza, invariancia UTC; elegida|
|Adjudicación dirigida por coste|Qué IDs adjudicar para estrechar intervalo|Optimizar adquisición informativa|Podría priorizar trabajo humano|Media, costes y calidad reales desconocidos|Baseline de selección aleatoria/fairness; pospuesta, no inventar presupuesto humano|
|DP de balance escalable|Guardias de30 y reconstrucción de testigos|Reducir memoria/tiempo|Útil para grandes snapshots|Alta, pero no cierra precondiciones semánticas|Comparadores bitset/optimización y contratos; pospuesta|

Continuidad del pilar02 ML engineering justificada: el negativo1nov era una precondición fácil de violar de la misma API; rotar ahora dejaría una herramienta reutilizable sin una barrera básica. No equivale a ignorar pilares restantes: se registra rotación pendiente tras cerrar procedencia/fechas y fuente real. No presentar metadata gate como avance en modelos fundacionales o IA agentic.

## Cinco fuentes primarias realmente abiertas2nov2026

|Clave BibTeX / URL|Problema y supuestos|Método/evidencia existente|Diferencia concreta y alcance de revisión|
|---|---|---|---|
|snapshot1102prov, https://www.w3.org/TR/prov-dm/|Procedencia de entidades/actividades/agentes|Recomendación W3C2013 de modelo de procedencia|Inspiración de campos explícitos; no implementar todo PROV ni certificar conformidad. Página primaria abierta; no auditoría normativa completa|
|snapshot1102datetime, https://docs.python.org/3/library/datetime.html|Instantes aware frente naive|Documentación oficial de fechas/offsets|Normalizamos UTC para comparar; no nuevo método temporal. Documentación estable abierta, código probado Python3.12, no requiere nuevas APIs de la documentación actual|
|snapshot1102feast, https://docs.feast.dev/getting-started/concepts/point-in-time-joins|Reproducir estado histórico de features|Documentación oficial point-in-time joins|Disciplina conocida as-of como baseline; no se usa Feast ni se atribuye garantía de disponibilidad a sus joins. Página primaria abierta|
|snapshot1102leakage, https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/|Fuga/reproducibilidad científica|Taxonomía y estudio propio de Kapoor/Narayanan2023|Motiva alcance limitado del control; no reproducimos estudio empírico ni acreditamos ausencia de toda fuga. Texto primario abierto|
|snapshot1102entity, https://arxiv.org/abs/2008.04443|Entity resolution y clustering de registros|Binette/Steorts revisión de métodos|No inferimos identidad: solo declaramos equivalencia en subconjunto como precondición. Resumen/metadatos abiertos; no revisión íntegra del PDF|

Aporte al repositorio: disciplina temporal/semántica ahora ejecutable y salida de procedencia durable; antes solo advertencia en docs1101. Frente a literatura, contrato y as-of son ingeniería conocida. Clasificación: **adaptación de ingeniería y auditoría**, sin novedad algorítmica/científica acreditada. Empatar referencia as-of es resultado esperado, no superioridad. Las cotas1nov y su derivación se preservan, no fórmula nueva decorativa. Búsqueda no exhaustiva de contratos/provenance/seguridad.
