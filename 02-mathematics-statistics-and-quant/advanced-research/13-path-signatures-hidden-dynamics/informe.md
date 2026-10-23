# 1. Título
Firma nivel 2 con certificado algebraico y frontera de observación.

## 2. Hipótesis y novedad incremental
Para pares de polígonos orientados que comparten puntos y marginales, la parte antisimétrica del nivel 2 conserva orden perdido por endpoints/momentos. Umbral previamente fijado en config: exactitud sin ruido >=0.95 y error contra oráculo <1e-10. La aportación local es convertir S1 en auditoría ejecutable con contraejemplos, no inventar firmas.

## 3. Estado del arte
Chevyrev–Kormilitzin presentan fundamentos; Lyons explica el homomorfismo; Hambly–Lyons prueban unicidad de la firma completa salvo tree-like. Reizenstein–Graham y Kidger–Lyons implementan bibliotecas mucho más generales y optimizadas. Cinco referencias primarias verificadas en fuentes.md; BibTeX en referencias.bib. No se afirma revisión exhaustiva.

## 4. Brecha
El programa 13 tenía diseño sin código. Faltaban controles para separar redondeo de cálculo, pérdida por muestreo y pérdida por truncamiento. El MVP cierra esa brecha para geometría finita en nivel 2, sin resolver dinámica oculta general.

## 5. Diseño y config
Semilla 422; 100 pares reversos por ruido 0, .05, .25, 1.0, círculos de 64 segmentos perturbados en coordenadas. Se fuerza cierre. La etiqueta es orientación latente anterior al ruido, no signo geométrico posterior: así el ruido puede causar errores genuinos. Endpoint/momentos son idénticos para cada par; el baseline determinista constante es óptimo sobre esos resúmenes en este diseño balanceado. 800 trayectorias no equivalen a 800 observaciones independientes: son 400 pares, 100 por nivel. No se calculan intervalos ingenuos sobre miembros dependientes.

## 6. Implementación real
`src/signatures.py` implementa S1 y S2 con composición de Chen; orden de multiplicación explícito. Para segmento v: S2 nuevo = S2 previo + S1 previo tensor v + v tensor v / 2. Tiempo O(nd²), estado recurrente O(d²); API batch recibe input O(nd), no se reclama streaming de entrada ni ahorro global sobre shoelace. El oráculo usa área poligonal cerrada; no comparte la recurrencia tensorial.

## 7. Tests y benchmarks
Siete tests de unittest pasan: cuadrado, 12 combinaciones aleatorias n/d con Chen/shuffle/reversión/traslación, trayecto tree-like, punto único, entradas inválidas aliasing y subdivisión colineal con punto estacionario. Coverage mide 100% de 37 sentencias del núcleo únicamente; no equivale a cobertura de todos los caminos ni de notebooks/benchmark. Ruff src/tests/ejecutor y mypy src pasan. No hay C/C++, por lo que sanitizers no aplican. Se preservan tiempos medianos de tres ejecuciones y pico de asignaciones Python tracemalloc (no RSS) por 64/256/1024/4096 segmentos y ambos métodos. Los tiempos dependen del hardware, no son garantía.

## 8. Resultados ejecutados

| Ruido | Firma nivel 2 | Endpoint/momentos |
|---|---:|---:|
| 0 | 100% | 50% |
| .05 | 100% | 50% |
| .25 | 100% | 50% |
| 1.0 | 70% | 50% |

Error máximo firma-área independiente: 1.0658e-14. Orden de convergencia geométrica final: 1.99987. Dos vueltas: área densa 6.2806623, submuestreo de cuatro segmentos 0. Figura `results/audit.png`; números crudos en CSV y summary.json.

## 9. Análisis crítico y ablaciones negativas
Quitar nivel 2 deja solo endpoint y destruye separación. Pero una simple área shoelace consigue el mismo estadístico planar y es más eficiente: no hay ventaja algorítmica frente a ese comparador. El caso tree-like ida/vuelta tiene firma nula pese a movimiento no trivial. El submuestreo borra área y nivel 2 no puede recuperarla. Ruido alto baja a 70%, refutando robustez universal. El orden O(h²) observado es error del polígono respecto al círculo, no mejora numérica de la recurrencia exacta para polígonos.

## 10. Límites, sesgos y madurez
Datos geométricos sintéticos deliberadamente favorables a una señal conocida. No hay aprendizaje, validación operacional, inferencia causal, reconstrucción ni evaluación financiera. Firma completa y truncada tienen garantías distintas. Componente S2, programa con alcance pendiente; no se declara S3 ni M2 automáticamente. EL=83 no aplica. El kernel Jupyter no pudo abrir sockets por restricción del entorno; el notebook fue ejecutado realmente con IPython in-process, namespace de script fresco, captura de resultados y errores; metadata lo declara. No se afirma ejecución en kernel separado.

## 11. Comando exacto
Desde esta carpeta: `bash run.sh` (Python 3.12; instalación más ejecución). Usa pip con dependencias fijadas; no requiere datos remotos. Se recomienda venv. `python scripts_notebook.py` regenera y ejecuta notebook.

## 12. Referencias BibTeX
Cinco entradas completas en `referencias.bib`, con URLs persistentes; alcance de lectura declarado en `fuentes.md`.

## 13. Rúbrica 1–5
Novedad 2 (auditoría local, teoría conocida); rigor 4 (oráculo/invariantes, sin prueba formal general); reproducibilidad 4 (pins, script, outputs, limitación kernel); código 4; claridad 4; impacto 3 (utilidad didáctica, sin evidencia real); honestidad 5; MVP ejecutable 4 (in-process real, no kernel aislado). Autoevaluación, no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: medir pérdida de orden y estabilidad bajo muestreo irregular y contrastar contra una biblioteca independiente.

1. `advanced-research/13-path-signatures-hidden-dynamics`: réplica con iisignature y mayor dimensión.
2. `advanced-research/13-path-signatures-hidden-dynamics`: curvas con mismo nivel 2 y distinto nivel 3.
3. `quantitative-methods/validacion-cruzada-temporal`: definir separación temporal antes de aplicar firmas a series reales.
