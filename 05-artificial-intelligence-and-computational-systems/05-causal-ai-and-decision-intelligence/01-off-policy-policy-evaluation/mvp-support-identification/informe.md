# CICLO_DIARIO IA — 26 de octubre de 2026

## 1. Título
Evaluación fuera de política con soporte deficiente: separar identificación estructural de precisión muestral.

## 2. Hipótesis, selección entre tres ideas y novedad incremental

| Idea | Decisión | Motivo |
|---|---|---|
| Auditor tabular OPE de soporte e identificación | Elegida | Rota al pilar causal 05, propuesta S1 sin código y contraejemplo verificable con mundos indistinguibles |
| Versionado de citas en RAG | Diferida | PR 78 de arquitectura legal/RAG reciente; evitar trabajo concurrente o duplicado |
| TTL y replay de recibos outbox | Diferida | Repetiría el pilar de orquestación del 24 de octubre |

Hipótesis fijada en config.json: cobertura empírica de la envolvente ≥95%, cero errores definitivos observados, ancho ≥0,40 en soporte deficiente y sesgo IPS del mundo alto ≤−0,30 con n=2.000. La contribución es una auditoría de identificación y reporting dentro del portafolio. No se inventa un estimador nuevo ni se reclama novedad mundial frente a literatura de soporte deficiente.

## 3. Estado del arte y referencias reales
Sachdeva, Su y Joachims (2020, arXiv:2006.09438) documentan la falla de IPS sin soporte y alternativas de restricción/extrapolación. Dudík, Langford y Li (2011, arXiv:1103.4601) combinan modelos de recompensa y propensión en evaluación doubly robust; esta implementación no replica su algoritmo. Swaminathan y Joachims (ICML 2015, PMLR 37:814–823) estudian minimización contrafactual y varianza; su trabajo NIPS 2015 sobre estimación autonormalizada motiva el baseline SNIPS. Jiang y Li (ICML 2016, PMLR 48:652–661) extienden evaluación DR a decisiones secuenciales, fuera del alcance contextual de un paso aquí.

Se abrieron las cinco páginas primarias (arXiv/PMLR/NeurIPS), verificando metadatos y resúmenes. No revisión exhaustiva ni replicación independiente de estos trabajos. La fórmula de concentración usa Hoeffding (1963); DOI verificado desde metadatos de búsqueda del editor, página del editor bloqueada 403 y PDF espejo del artículo original abierto, sin extracción de texto. Se conserva esa limitación en el registro de fuentes. Seis entradas BibTeX reales, cinco OPE verificadas directamente; sin DOI inventados.

## 4. Brecha identificada en main
Se inspeccionó main 674699d y la propuesta 05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation, todavía S0/S1. El único PR abierto al inicio era #83 de ideas de riesgo; no se modifica su dominio. Los aportes previos eran conformal predictivo, outbox y conformidad de trazas. Aquí la pregunta es el valor de una intervención que el logger no ejecuta: no intervalos de predicción individual ni orden de eventos.

La propuesta amplia incluye IPS/SNIPS, DR, cross-fitting, datasets públicos y diagnóstico de overlap. Se reduce a un MVP tabular de soporte conocido; DR, datos reales y logging secuencial siguen pendientes, sin presentar toda la propuesta como concluida.

## 5. Diseño experimental y configuración
Tres contextos con masa poblacional p=(0,40; 0,20; 0,40), dos acciones y recompensa Bernoulli. La política objetivo usa probabilidad 0,5 para cada acción en contextos 0/1 y acción 1 con probabilidad 1 en contexto 2. Medias de recompensa: (0,2; 0,6), (0,4; 0,8), (0,5; θ), con θ=0 o θ=1.

Logger deficiente: acciones equiprobables en contextos 0/1; sólo acción 0 en contexto 2. Logger de control: ambas acciones con probabilidad 0,5 en todos los contextos. En el régimen deficiente, los mundos θ=0 y θ=1 generan exactamente el mismo log usando la misma semilla, pero el valor objetivo es 0,28 o 0,68. Se verifica igualdad de listas observadas y se guardan huellas SHA256; la verdad sólo se usa para evaluar, no se entrega al auditor.

40 semillas × dos tamaños (200/2.000) × dos regímenes × dos mundos = 320 evaluaciones de diseño, cuatro políticas de reporting = 1.280 filas. Las parejas de mundos no son independientes; no se tratan como 320 réplicas independientes para intervalos Monte Carlo. Logs de ejemplo, estadísticas suficientes por celda y recursos se conservan; el generador y semillas reproducen todos los logs sin guardar datos redundantes gigantes.

Supuestos: distribución poblacional de contextos conocida, logger randomizado conocido y fijo, objetivo fijo independiente de datos, recompensas IID condicionales a contexto/acción en [0,1], tamaño muestral fijo. No confusión no observada ni adaptación de logging en este generador. Fuera de estos supuestos no se interpreta como identificación causal válida.

## 6. Implementación y garantía local
src/evaluation.py valida vectores de probabilidad, índices, rango de recompensa y que ningún evento observado sea imposible bajo el diseño declarado. Agrega conteos y sumas por celda. Masa no soportada = suma de p(x)π(a|x) donde μ(a|x)=0; masa soportada no vista = peso de celdas con μ>0 y conteo cero. No confunde ausencia muestral con probabilidad estructural cero: esta última proviene de un contrato conocido del logger.

Para cada celda con n>0, radio r=sqrt(log(2CA/δ)/(2n)), intervalo [max(0,media−r), min(1,media+r)]. Celda no vista, estructural o muestral, conserva [0,1]. Se ponderan extremos por pπ y se suman. Condicionado a las asignaciones, Hoeffding por celda y unión sobre CA dan cobertura ≥1−δ de todas las medias, y por pesos no negativos de su valor agregado. Es cobertura de muestra fija bajo diseño conocido, no secuencia de confianza, ni validez tras selección de política, ni garantía con propensiones/contextos estimados.

Con datos ilimitados y medias soportadas conocidas, la región de identificación es [0,28; 0,68]. Es nítida: variar θ continuamente entre 0 y 1 no cambia la distribución observada y alcanza cualquier valor dentro. Su ancho 0,40 es una incertidumbre estructural que más logs del mismo logger no elimina. La envolvente finita añade incertidumbre muestral y por eso es más ancha.

Complejidad del evaluador: O(n+CA), memoria de trabajo O(CA), excluida la lista de observaciones suministrada. Las estadísticas de benchmark sólo miden esa evaluación, no generación ni serialización.

## 7. Tests y benchmarks ejecutados
11 tests: no identificación estructural, ausencia finita no estructural, objetivo que sí tiene soporte aunque otra acción carezca de él, 100 propiedades aleatorias del piso de ancho/rango, contracción con observaciones constantes, log vacío, media ponderada conocida, rechazo de evento imposible, entradas inválidas, mundos observacionalmente idénticos y fronteras de decisión. Comando `python -m unittest discover -s tests -v`. Ruff en src/tests/benchmarks y mypy del núcleo con configuración local pasan. Cobertura de líneas no medida. C++/sanitizers no aplican.

Benchmark ejecutado con semilla, tamaño y mundo explícitos en CSV; cuentas/sumas/huellas y recursos en JSONL; resúmenes y hardware/versiones en JSON. Tiempo y pico tracemalloc son del evaluador compuesto, no latencia comparativa de cada baseline. Trazado excluye memoria de entrada y buffers nativos; no equivale a RSS total. No se afirma coste cloud ni rendimiento de un servicio.

Notebook de cuatro celdas ejecutado secuencialmente por IPython in-process, con outputs reales y validación nbformat; no kernel Jupyter aislado. Ambas figuras SVG se renderizaron con sharp a PNG y se inspeccionaron: texto legible, sin recortes. El revisor independiente reproduce el comando integral antes de publicación; su resultado se reporta separado de pruebas del autor.

## 8. Resultados con números y figuras
Resultados n=2.000, 80 evaluaciones por régimen (40 pares de mundos):

| Régimen y método | RMSE del punto | Errores de decisión / total | Decisiones | Cobertura envolvente | Ancho medio |
|---|---:|---:|---:|---:|---:|
| Deficiente, IPS truncado | 0,28186 | 50% | 100% | No aplica | No aplica |
| Deficiente, SNIPS en soporte | 0,20075 | 50% | 100% | No aplica | No aplica |
| Deficiente, midpoint | 0,20012 | 50% | 100% | No aplica | No aplica |
| Deficiente, envolvente | No aplica | 0% | 0% | 100% observado | 0,51307 |
| Completo, IPS | 0,01431 | 0% | 100% | No aplica | No aplica |
| Completo, SNIPS | 0,01013 | 0% | 100% | No aplica | No aplica |
| Completo, midpoint | 0,00690 | 0% | 100% | No aplica | No aplica |
| Completo, envolvente | No aplica | 0% | 100% | 100% observado | 0,14608 |

Umbral de decisión fijo 0,50. En soporte deficiente las tres cifras puntuales son iguales entre mundos y cada pareja debe equivocarse en uno: el 50% no es una prevalencia poblacional estimada. La envolvente se abstiene en ambos y **no obtiene 80 decisiones acertadas**. Su cero errores es cero afirmaciones definitivas; el control con soporte completo muestra utilidad al permitir decisiones cuando existe evidencia.

A n=200, ancho deficiente 0,72666 y completo 0,43251; ambos se abstienen en todas las réplicas. La envolvente conservadora sacrifica utilidad con muestras pequeñas. En deficiente el sesgo medio de midpoint es ~0,00066 al mezclar mundos, pero RMSE ~0,20: sesgos opuestos se cancelan. IPS en mundo alto tiene sesgo ~−0,3984; no se salva normalizando pesos. Cobertura observada 100% no certifica cobertura fuera del generador; δ=0,05 es por evaluación, no simultánea en todos los 320 experimentos.

Figuras: results/support.svg separa errores de abstenciones; results/width.svg muestra contracción con n y piso estructural 0,40. Recursos exactos de la última reproducción en summary.json. Corrida inicial: ~1,7 ms para n=200 y ~14 ms para n=2.000; trabajo aproximadamente lineal. Memoria trazada del evaluador ~1–2 KB, sin contar la entrada, por lo que no es estimación del consumo total del pipeline.

## 9. Análisis crítico y ablaciones negativas
IPS truncado se calcula sobre acciones observadas, pero sin soporte no estima el valor completo de la política. Se etiqueta así explícitamente, sin reclamar insesgamiento. SNIPS normaliza por el peso observado y aproxima el valor condicionado al soporte; tampoco inventa la recompensa que falta. Midpoint añade 0,5 a cada media ausente: es una hipótesis de extrapolación, no información del log ni una implementación de DR.

Comparar puntos contra una envolvente por RMSE sería engañoso; se reportan productos diferentes y tasa de decisiones junto al error. La envolvente no siempre mejora utilidad: con n=200 y soporte completo se abstiene aunque los puntos aciertan en las réplicas. El control positivo identifica esa limitación. Aumentar muestra resuelve precisión cuando hay soporte, pero no rompe equivalencia observacional con ceros estructurales.

No se eligió threshold después de observar resultados ni se ajustaron parámetros para rescatar la hipótesis. La regla δ fija es conservadora; podrían estudiarse intervalos más eficientes, conservando requisitos de identificación. No se evaluó aprendizaje de política, recompensa modelada ni heterogeneidad oculta.

## 10. Limitaciones, riesgos y madurez
Sin propensiones estimadas, contextos poblacionales estimados, logging adaptativo, confusión no medida, políticas aprendidas con el mismo log, recompensas fuera de [0,1], horizonte secuencial o datos reales. El núcleo general acepta finitos contextos/acciones; el experimento concreto usa tres contextos y dos acciones con medias conocidas para contrastar verdad. El soporte conocido es un supuesto fuerte: no se certifica a partir de un conteo cero.

Usar una envolvente estrecha con logger mal declarado puede dar falsa seguridad. No hay permisos, sistema operacional ni recomendaciones automáticas para clientes; todos los datos son sintéticos sin información personal. No habilita experimentación de acciones en personas sin un proceso aparte aprobado. No se inventan afirmaciones regulatorias.

Componente S1→S2 ejecutado, candidato M2 local sujeto a revisión técnica independiente. El programa completo sigue parcial y no es un sistema validado u operacional. El uso de IPython in-process es explícito; no se afirma validación mediante kernel aislado.

## 11. Cómo correrlo
Desde `05-artificial-intelligence-and-computational-systems/05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation/mvp-support-identification`:

`bash run.sh`

Python 3.12 + pip. Instala requisitos de notebook fijados, ejecuta tests, experimento y notebook. Núcleo sólo biblioteca estándar. Entorno preinstalado: `PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" SKIP_INSTALL=1 bash run.sh`. Los cálculos no requieren API/red; pip sí necesita paquetes disponibles.

## 12. Referencias BibTeX
Seis entradas en referencias.bib, con cinco trabajos OPE primarios abiertos y verificados. Hoeffding tiene DOI real y límite de acceso documentado; se abrió espejo original sin extracción de texto. Registro con fecha 26-10-2026 y URLs en results/references_verified.json. No se presentan las citas como experimentos ejecutados por este MVP.

## 13. Rúbrica 1–5
Novedad 2 (diagnóstico adaptado de literatura existente), rigor 4 (mismos logs/dos mundos, supuestos y garantía local), reproducibilidad 4 (semillas/estadísticas/outputs, ejecución in-process), código 4 (núcleo tipado y 11 tests), claridad 4, impacto 3 (previene certeza injustificada sin evidencia operativa), honestidad 5, MVP 4 (ejecutable completo acotado). Autoevaluación; no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: separar soporte pequeño positivo de soporte cero y evaluar cuándo un modelo de recompensa aporta una extrapolación defendible.

1. 05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation: incorporar logging con soporte mínimo positivo decreciente y evaluar varianza sin confundirlo con no identificación.
2. 05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation: comparar DR con modelos de recompensa correctos y mal especificados, con cross-fitting y límites explícitos en ausencia de soporte.
3. 08-ai-reliability-security-and-governance: registrar contratos de propensión/selección de política y bloquear usos de confianza incompatibles con logging adaptativo o parada opcional.
