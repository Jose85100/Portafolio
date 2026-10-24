# Calibración KYC contaminada — CICLO24oct2026

## 1. Título
Envolvente conservadora del rango con presupuesto externo de contaminación.

## 2. Hipótesis y novedad
Bajo contaminación de scores bajos, guard con cota correcta tendrá FPR media≤5,5% y reducirá FPR ordinaria al menos2pp. Umbral fijado en config antes del benchmark. Es una auditoría incremental local, no un nuevo teorema de la literatura. El ciclo23oct estudió referencia limpia por canal; este aísla contaminación en un único canal.

## 3. Estado del arte
Cinco fuentes primarias verificadas24oct: Bates (p-valores marginales/dependencia); Angelopoulos/Bates (rangos); Clarkson et al. (contaminación); Bashari et al. (robustez conservadora y limpieza activa); Barber et al. (deriva). Referencias.bib y benchmarks/prior-art.md. No se implementa CRCP ni limpieza activa; no se afirma revisión exhaustiva.

## 4. Brecha
La calibración por canal existente no contempla que etiquetas inlier de referencia sean erróneas. Un contaminante con score bajo no es necesariamente fácil de identificar; eliminar scores altos no soluciona esa amenaza y puede cambiar la ley limpia.

## 5. Diseño
80 semillas0–79; n499; c199 en escenarios contaminados; 2.000 inliers y500 anomalías de prueba por semilla. Score fijo |Normal|, anomalías |Normal(3,1)|, inliers |Normal(0,1)|. Contaminantes todos0 o100 son estrés adversarial, no prevalencia real de fraude. Clean usa c0 pero cota conservadora199. Low usa c199/m199; understated usa c199/m99. Baseline ordinario equivale m0 con exactamente mismos scores/splits. Datos calibración/prueba independientes. Los mismos conjuntos de prueba se reutilizan entre políticas para comparación emparejada.

## 6. Método y argumento
Sea n total, c≤m contaminantes, k conteo observado≥s y k0 conteo limpio. p_guard=min(1,(1+k)/(n−m+1)). Puesto que k≥k0 y n−m≤n−c, p_guard≥p_limpio=(1+k0)/(n−c+1). Entonces evento{p_guard≤α}⊆{p_limpio≤α}. Si el subconjunto limpio (no elegido adaptativamente por score) y próximo inlier son intercambiables para score congelado, la validez marginal limpia se transmite al guard. Empates con≥ son conservadores. Se permite contaminación arbitraria, pero no eliminación adaptativa de observaciones limpias que invalide intercambio. La cota es externa y debe cumplirse; no se certifica desde los datos de este MVP. Para cota aleatoria, sería necesaria garantía conjunta adicional; no se proporciona.

## 7. Tests y benchmarks
Cinco tests incluyendo oráculo, identidad m0, dominación exhaustiva en muestras discretas con0..2 contaminantes, leave-one-out superuniforme con empates, monotonicidad y entradas/cotas inválidas. Cobertura núcleo23 sentencias100%; no se mide cobertura del experimento. Ruff src/tests/benchmarks y mypy estricto núcleo. Benchmark rendimiento n100/1000/10000,10.000 consultas; tiempos crudos en performance.csv, no inferencia causal de complejidad a partir de tres tamaños. Tiempo total/memoria Python medidos con tracemalloc, plataforma y versiones metrics.json. C++ no aplica.

## 8. Resultados
| Escenario | FPR ordinario | FPR guard | Detección ordinaria | Detección guard |
|---|---:|---:|---:|---:|
| Limpio, cota excesiva |5,018%|3,091%|84,877%|79,543%|
|199 scores bajos, cota199|8,346%|5,007%|89,578%|84,740%|
|199 bajos, cota99 errónea|8,346%|6,763%|89,578%|87,528%|
|199 scores altos|0%|0%|0%|0%|
Hipótesis supera umbral: reducción3,339pp, guard5,007%. Summary incluye SE entre80 semillas; barras±1,96SE para media Monte Carlo, no intervalo de FPR operacional. Calibración compartida genera dependencia dentro de cada semilla; no se finge independencia de todas las observaciones. Una FPR observada5,007% no refuta cota probabilística5% por error Monte Carlo.

## 9. Crítica y ablaciones negativas
Cota subestimada falla nominal; cota excesiva pierde potencia en limpio; contaminación alta anula detección en ambos métodos, no mejora universal. Un score de identidad muy bajo podría representar normalización/adversario o error de calidad: escenario no demuestra frecuencia real. Baseline no es un detector ML: pregunta estudia calibración con score idéntico. Validar guard no valida el score.

## 10. Límites y riesgos
No hay datos bancarios ni garantía individual, FDR de lote o estimación de fraude. No se valida deriva, selección por aprobación, etiquetas tardías, canales desbalanceados, incertidumbre de m o dependencia temporal. No se usa para rechazar crédito automáticamente. Cota externa puede ser impracticable; sin certificarla no se reclama garantía. Score entrenado en calibración violaría el contrato.

## 11. Reproducir
`bash run.sh`: instalación y ejecución, notebook IPython secuencial con outputs reales. SKIP_INSTALL1 opcional. Versiones directas fijadas; no lock completo de transitivas. Figura inspeccionada por separado; no renderHTML completo. No se simula kernel.

## 12. Referencias
Cinco entradas reales verificadas, páginas primarias y alcance en referencias.bib y benchmarks/prior-art.md. Derivación elemental local separada de claims de artículos.

## 13. Rúbrica
Autoevaluación no certificación: novedad2/5, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4. Prototipo sintético de componente; revisión independiente del ciclo aparte. No se elevan dominios.

## 14. Siguiente iteración
Siguiente iteración recomendada: certificar una cota de contaminación a partir de auditoría humana con presupuesto explícito. Tareas: (1) contamination-budget-audit: ampliar a cota aleatoria con error de certificación; (2) channel-conformal-audit: validar temporalmente por canal; (3) loss-minimization-engine: comparar costes humanos y potencia perdida antes de piloto.

## Checklist
Código/comando/tests/baseline/salidas/figura/notebook ejecutado/README/informe/BibTeX/MVP/config/dependencias presentes. Revisión y publicación solo se afirman con evidencia posterior.
