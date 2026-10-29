# Informe crítico: holdout por componentes vinculados

1. **Título.** Cierre transitivo de identidad antes de evaluar ML.
2. **Hipótesis y novedad incremental.** En cadenas A–AB–B, una clave sola puede filtrar identidad. H: componentes completos producen cero cortes en los144 pares grupo/seed; falsable mediante auditoría. No algoritmo nuevo ni prioridad mundial.
3. **Estado del arte.** Kapoor/Narayanan documentan fugas; sklearn recomienda grupos y separar transformación de test; NetworkX define componentes; hashlib permite orden fijo. Cinco fuentes primarias verificadas en referencias.bib y results/references_verified.json, cuatro documentales y un artículo.
4. **Brecha.** Evaluación por fila y por clave directa omiten relaciones transitivas. Se rotó desde RAG28 a ML engineering; caché y scheduler se descartaron por cercanía con proyectos existentes. No sustituye conformal ni support/OPE anteriores.
5. **Diseño/config.** config.json registra12 seeds,36 filas,12 cadenas aisladas de3 filas; sin datos reales ni labels. Cada política asigna mitad de sus grupos a train por hash. CPU local Linux; versiones fijadas. La identidad se considera no sensible solo porque es sintética.
6. **Implementación.** src/splitter.py valida IDs, construye índice token→filas, recorre componentes, etiqueta con menor ID y hace holdout. Orden fijo independiente del input. Complejidad incluye ordenación O(N log N), recorrido incidencias esperado lineal y hash de claves; sin escalabilidad medida. Una componente única falla explícitamente.
7. **Tests/benchmarks reales.**10 tests unitarios,100 permutaciones y100 seeds de invariantes; lint ruff y mypy estricto del núcleo. raw.csv guarda36 ejecuciones. Tiempos/peak son una ejecución instrumentada, no speedup robusto; cobertura líneas no medida. Sanitizers/CMake no aplican Python.
8. **Resultados/tablas/figuras.**

|Política|Cortes/144|train/36|
|---|---:|---:|
|fila|108|18|
|primaria|70|17–20|
|componente|0|18|

results/leakage.svg visualiza cortes; summary.json contiene tiempos y memoria reales. No hay precisión predictiva estimada. Notebook ejecutado con4 celdas reales y outputs por IPython en proceso.

9. **Análisis crítico/ablación negativa.** Quitar cierre transitivo (primary) deja70 cortes; quitar agrupación (row),108. Ambas negativas son reglas implementadas, idéntico corpus y seeds. No se demuestra que hashing sea mejor que stratification ni que0 cortes mejore AUC. El corpus facilita grupos iguales y no representa desbalance real.
10. **Limitaciones/sesgos.** Solo se protege el grafo declarado. Vínculos falsos fusionan poblaciones; faltantes dejan fuga. Menor ID como representante cambia al añadir registros: se requiere snapshot congelado. No balance por clase ni tiempo; hashes no anonimizan identidades ni garantizan privacidad. Vínculos derivados de etiquetas o datos futuros introducen otras fugas. En producción requiere adjudicación y corpus externo.
11. **Comando exacto.** `bash run.sh` desde mvp-linked-entity-holdout; crea venv e instala requirements.txt. Ejecución verificada sin reinstalar: `PYTHON=/workspace/scratch/6c8b818bd733/ia28-env/bin/python SKIP_INSTALL=1 bash run.sh`.
12. **Referencias BibTeX.** referencias.bib contiene5 URLs verificadas; no DOI inventado. Método clásico de componentes; no se afirma novedad teórica.
13. **Rúbrica1–5.** Novedad2, rigor3, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4; autoevaluación no certificación. Prototipo local ejecutado, revisión independiente reprodujo comando completo y núcleo sin bloqueantes el 2026-10-29; ni validación externa ni operacional. No S2=M2.
14. **Siguiente iteración.** Incorporar identidades adjudicadas y benchmark con tamaños desiguales; estudiar restricción temporal sin usar enlaces futuros; rechazar componentes gigantes con criterio de negocio explícito. Continuar por cero cortes; ajustar por desequilibrio; cerrar uso si links no confiables o holdout vacío.
