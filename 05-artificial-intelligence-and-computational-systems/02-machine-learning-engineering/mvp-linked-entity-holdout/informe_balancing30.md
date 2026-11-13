# Informe30: profundización del holdout por identidad

1. **Título.** Balance exacto por masa de filas conservando identidades transitivas.
2. **Hipótesis/novedad.** Extensión del negativo29 de tamaños iguales. H: desviación DP <= baseline factible en25/25 comparaciones y0 cortes. Adaptación ingenieril de subset-sum conocido; no método ML original.
3. **Estado del arte.** prior_art30.md clasifica5 referencias primarias abiertas30:3docs oficiales,1artículo arXiv y1curso MIT. GroupShuffleSplit cuenta grupos y GroupKFold ya aborda grupos/balance: no se oculta esa cercanía. No comparamos directamente sklearn ni afirmamos superioridad universal.
4. **Brecha.**29 reportó108/70/0 cortes en corpus igual; no balance de filas. Tres ideas comparadas: masa (elegida), links falsos/faltantes, temporalidad (roadmap). No nuevo demo aislado: reutiliza components, Record, auditor y tests29 intactos.
5. **Diseño/config.** config_balancing.json, cinco corpora de4 grupos y ratios1/4,1/3,1/2,2/3,3/4. Sin datos ni etiquetas reales. Baseline generaliza conteo29 con floor(Kp/q) y clamp no vacío; mismo objetivo solicitado, vínculos y corpus. Seed baseline0 no optimizada; DP sin seed. Seis mediciones adicionales10/30/60 grupos. Snapshot congelado, CPU local, versiones fijadas existentes.
6. **Implementación y derivación.** src/balancing.py, derivacion30.md y notebook con LaTeX: minimizar |qs-pN| sobre sumas alcanzables propias, DP con snapshots evita reutilización; testigo determinista. Fórmula exportada J=|qs-pN|/q en filas. Empate menor masa, no lexicográfico global. Conservador O(K²N) tiempo/O(KN) memoria por tuplas, más grafo. Guardias2000filas/100componentes son alcance, no SLA.
7. **Tests/benchmarks reales.**21 tests totales29+30; oracle exhaustivo de todos subconjuntos en100 casos pequeños aleatorios,50 permutaciones, invariantes, ratios ilegales, guardias, grupo único y gigante. Ruff, mypy estricto2núcleos.50runs de sensibilidad y6 de escala; raw.csv/scale.csv conservan tiempo/peak medidos. Cobertura líneas no medida; sin C++ ni sanitizers aplicables. Notebook6celdas reales IPython secuenciales, no kernel independiente.
8. **Resultados/tablas/figuras.**20 mejoras,5 empates,0 peores de25pares;0 cortes. Desviación media3.5067 a2.0133 filas. Figura balance.svg y resultadosJSON/CSV. A r=1/2:

|Tamaños|Conteo J(filas)|Exacto J(filas)|
|---|---:|---:|
|3,3,3,3|0|0|
|1,1,1,9|4|3|
|1,2,3,10|5|2|
|2,3,7,8|5|0|
|1,1,1,30|14.5|13.5|

Escala medida hasta291filas/60grupos. Tiempos/memoria de una pasada instrumentada en summary.json; DP tiene mayor coste y no se afirma speedup. Métrica es error de masa, no error de predicción.

9. **Análisis crítico/negativos.** El óptimo garantiza no empeorar objetivo respecto cualquier baseline factible, luego20/25 no es sorpresa ni validación empírica.5empates muestran ausencia de ventaja en casos; gigante33filas deja13.5filas irreducibles. Una sola componente se rechaza. Quitar optimización (conteo) es ablación legítima; baseline no se ajustó para quedar mal. Falta múltiples seeds baseline, optimizadores externos y grupos reales.
10. **Limitaciones/sesgos.** Enlaces provistos, falsos/faltantes no evaluados. Generación del grafo puede usar información futura; no split temporal. Cantidades de clase, representatividad y desempeño no se optimizan. IDs nuevos pueden cambiar componente representante: no asignación incremental estable. Límites son escala pequeña; selección por metadata no permite seleccionar por labels/test AUC. Ningún claim causal, privacidad o uso financiero real.
11. **Comando exacto.** Desde este proyecto: `bash run_balancing.sh`. Verificado `PYTHON=/workspace/scratch/6c8b818bd733/ia28-env/bin/python SKIP_INSTALL=1 bash run_balancing.sh`. Dependencias fijadas en requirements.txt, CPU/Linux/Python3.12.14, sin APIs externas; pip inicial requerido.
12. **Referencias BibTeX.** Entradas groups30,kfold30,components30,leakage30,dp30 en referencias.bib; URLs y fecha en results/balancing30/references_verified.json. No cinco papers ni DOI ficticio.
13. **Rúbrica1–5.** Novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4 (autoevaluación). Prototipo local ejecutado; revisión independiente reprodujo pipeline, núcleo, unidades y figura sin bloqueantes2026-10-30. No validación externa/operacional, no promoción del programa ni equivalencia S2=M2.
14. **Siguiente iteración.** research-log.md/roadmap.md mantienen negativos y decisiones. Añadir links adjudicados a tests/test_balancing.py; restricciones de disponibilidad en src/splitter.py; ampliar escala/presupuestos en src/balancing_experiment.py. Continuar con0 cortes; ajustar si la masa no es tolerable; cerrar despliegue si links/fecha no auditables.
