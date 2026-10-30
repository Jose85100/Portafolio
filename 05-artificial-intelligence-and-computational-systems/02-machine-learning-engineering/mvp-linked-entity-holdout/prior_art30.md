# Matriz de prior art: clasificación honesta

Referencias abiertas el2026-10-30; claves BibTeX en referencias.bib. No se afirma descubrimiento del algoritmo ni mejor método universal.

|Clave|Tipo/aporte existente|Relación y diferencia local|Clasificación del aporte|
|---|---|---|---|
|groups30|Documentación sklearn: test_size cuenta grupos, no muestras|Nuestro baseline generaliza29 por proporción de grupos; no llama sklearn ni reproduce su aleatoriedad|Adaptación de ingeniería|
|kfold30|Documentación GroupKFold: folds con grupos no superpuestos; balance depende configuración|No afirmamos inventar balance; resolvemos objetivo exacto de un holdout por masa, sin kfold|Objetivo local distinto; sin comparación directa|
|components30|NetworkX: componentes de grafo no dirigido|Reutilizamos cierre transitivo29, sin dependencia NetworkX|Aplicación conocida|
|leakage30|Artículo Kapoor/Narayanan: fugas y reproducibilidad|Motiva revisar unidad de split; no prueba fiabilidad de links sintéticos|Motivación metodológica|
|dp30|Curso MIT: programación dinámica/knapsack|Subset-sum clásico con reconstrucción, guardias y objetivo racional exacto|Implementación clásica, no novedad algorítmica|

Gap cerrado:29 solo usó tamaños iguales;30 hace visible desequilibrio, optimiza la masa y conserva negativos irreducibles. No es algoritmo nuevo, teorema de generalización ni estudio empírico del negocio. Faltan comparación con optimizadores externos y datos adjudicados.
