# Informe de investigación — reducción de momentos, 4-nov-2026

## 1. Título y línea acumulativa
MOMENTS: árbol balanceado determinista para fusionar resúmenes dinámicos, sobre Welford/Chan y transporte MOMENTS_V1 de ciclos previos.

## 2. Hipótesis falsable y aporte
Para los DGP sintéticos fijados en `config_reduction.json`, cada árbol (left, reverse, balanced) tendrá error SD frente a Decimal menor o igual a `max(4 ulp,1e-12 relativo)`. Es prueba de precisión local, no hipótesis de superioridad general. Clasificación: adaptación de ingeniería y auditoría, no contribución científica original.

## 3. Estado del arte
Cinco referencias con matriz de método, supuestos y diferencia en `prior_art_reduction.md`; bibliografía en `references_reduction.bib`. La literatura incluye acumuladores verdaderamente reproducibles; el método presente no compite con su independencia de orden.

## 4. Brecha y tres alternativas
(a) usar cualquier orden disponible, sin repetibilidad fija; (b) reproducible accumulator exacto, más coste y cambios de estructura; (c) árbol fijo balanceado con Chan, seleccionado por ajuste al API y simplicidad. Se mantienen como controles fold directo y orden inverso.

## 5. Diseño/configuración
3 semillas (1104–1106), tamaños 256 y 4096, chunk=32, Gaussian sintético alrededor de 1e8 con desviación 0.01; oráculo Decimal de los mismos float64. El tiempo registra sólo la fusión del árbol y no la ingestión. Sin dataset externo, la simulación no es evidencia empírica.

## 6. Fórmula e implementación
Para A,B disjuntos, `n=nA+nB`, `delta=muB-muA`, `mu=muA+delta*nB/n`, `Q=QA+QB+delta^2*nA*nB/n`. Se deriva expandiendo `sum(x-mu)^2` por bloque; los términos cruzados desaparecen porque las desviaciones respecto de cada media suman cero. `variance=Q/(n-ddof)`, `SD=sqrt(variance)`. El código sólo determina en cada nivel los pares adyacentes; no cambia Chan ni la representación física.

## 7. Tests/benchmark
`tests/test_reduction.py`: identidad, orden repetido, y Decimal en 5 escalas. `benchmark_reduction.py`: 18 observaciones de ejecución sobre combinaciones seed×n×method. Ejecutar `bash run.sh`; los artefactos exactos y lint/tipos/coverage/C++ acumulativos quedan en `results/`.

## 8. Resultado
La hipótesis local pasó en los datos generados por el script: error absoluto máximo observado contra Decimal `5.204170427930421e-18`; spread máximo entre árboles `6.938893903907228e-18`. El mínimo/mediana/máximo de error y cada fila están en JSON/CSV. Estas cifras son dependientes del DGP y hardware.

## 9. Crítica y ablations
La principal ablación es fold izquierdo y reverso bajo las mismas particiones. El balanced tree fija orden para un mismo orden de chunks; permutar chunks puede cambiar bits. Dado que los errores son ya cercanos a cero en este DGP, no se prueba mejora material sobre baseline. No se seleccionan parámetros tras ver los resultados.

## 10. Limitaciones y sesgos
Simulación Gaussian en un solo rango alto; no datos productivos, no benchmark de escalabilidad extensivo, no cota universal, no invariancia de permutación ni medición RSS. Supone chunks disjuntos y orden canónico controlado por el llamador.

## 11. Comando reproducible
Desde la carpeta `02-mathematics-statistics-and-quant/quant-libraries/streaming-moments`: `bash run.sh`. Instala pins y reproduce pruebas, C++ acumulativo, benchmark y notebooks.

## 12. Referencias BibTeX
Cinco entradas DOI verificadas en `references_reduction.bib` y su matriz comparativa.

## 13. Rúbrica original (1–5)
Novedad 1; rigor 3; reproducibilidad 4; código 3; claridad 4; impacto 2; honestidad 5; MVP 3.

## 14. Rúbrica ampliada y siguiente iteración
Profundidad teórica 2; aporte defendible 2; calidad experimental 3; utilidad 3; reproducibilidad 4; honestidad 5. Continuar sólo si orden estable reduce variabilidad en múltiples DGPs y tamaños; siguiente prueba: rangos mixtos con contraste al acumulador reproducible exacto.

Madurez: prototipo ejecutable local, candidato a M2 de componente tras revisión independiente; no elevar dominio/programa completo ni M3.
