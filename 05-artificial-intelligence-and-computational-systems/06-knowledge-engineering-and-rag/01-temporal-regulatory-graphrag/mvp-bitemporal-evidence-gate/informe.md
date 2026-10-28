# CICLO_DIARIO IA — 28 de octubre de 2026

## 1. Título
Gate bitemporal de evidencia: separar aplicabilidad del hecho y estado conocido por el sistema.

## 2. Hipótesis, tres ideas y novedad incremental

| Idea | Decisión | Razón |
|---|---|---|
| Gate bitemporal de evidencia | Elegida | Rota al pilar 06, propuesta temporal S1 sin implementación y fixtures exactas pequeñas |
| Caché LRU de recuperación | Diferida | Routing/cache ya tiene código; menor novedad dentro del repositorio |
| Memoria con TTL | Diferida | Próxima a outbox de ciclos anteriores |

Hipótesis fijada: bitemporal devuelve cero citas definitivas incorrectas y cero fugas de conocimiento futuro; latest y valid_only tienen fugas; conflicto no devuelve cita. La contribución es integración y falsificación de un filtro antes de RAG, no un algoritmo bitemporal nuevo ni un GraphRAG completo.

## 3. Estado del arte con cinco fuentes verificadas
Snodgrass, Developing Time-Oriented Database Applications in SQL, explica valid time y transaction time; el PDF del autor muestra copyright 2000 y capítulo de tablas bitemporales. PostgreSQL 18 documenta rangos inclusivos/exclusivos y límites abiertos. Microsoft explica system-versioned temporal tables: ese tiempo del sistema no equivale automáticamente a validez de negocio. Lewis et al. (2020, arXiv:2005.11401) combinan recuperación y generación; aquí no se replica el modelo neuronal. W3C PROV-DM (2013) fundamenta identidad y procedencia, sin que este MVP implemente la especificación completa.

Se abrieron las cinco fuentes primarias y se comprobaron conceptos/metadatos relevantes. La página Microsoft mostró banner genérico de autorización, pero su contenido público pertinente era legible. Sin revisión exhaustiva ni cinco papers supuestamente nuevos. BibTeX y registro de fuentes incluidos; no se inventan DOI.

## 4. Brecha y revisión inicial
Se inspeccionó main 5b7d30e, sin PR abiertos al inicio. Se creó worktree aislado wt-ia28 y rama research/2026-10-28-cycle-ia. La propuesta 06-knowledge-engineering-and-rag/01-temporal-regulatory-graphrag era S0/S1; el evaluador RAG existente no contiene este gate de dos relojes. No se modifican sus bibliotecas, shared ni contratos globales. Se reduce la propuesta amplia a metadata por clave: grafo, normas reales, embeddings, entailment y generación quedan pendientes.

## 5. Diseño experimental y configuración
Ocho variantes × siete consultas × tres políticas = 168 evaluaciones, 56 por política. Casos: antes del primer registro, conocimiento antiguo, corrección retroactiva, validez futura con conocimiento antiguo, ambos nuevos, expiración y conflicto. Las variantes sólo cambian identidad/contenido sintético; no son muestras independientes de preguntas naturales.

Una versión inicial indica threshold=10+semilla y se conoce desde enero hasta marzo. En marzo se registra corrección retrospectiva para enero (12+semilla) y una regla para febrero en adelante (20+semilla), que expira en enero siguiente. Un caso añade una versión contradictoria solapada. Los intervalos se proporcionan explícitamente; la ingesta que crea/cierra esos rectángulos no se implementa. Cada consulta tiene estado y versión esperados manuales, independientes del filtro.

Todos los textos dicen SYNTHETIC ONLY, con sources synthetic://. Ninguna regla representa SFC/SBS/IFRS ni una obligación legal. known_from/to significa registro/conocimiento local, no necesariamente publicación oficial ni conocimiento universal. Fechas diarias canónicas YYYY-MM-DD, extremos [inicio,fin), fin None abierto. Valid_on y known_on son preguntas distintas; puede consultarse aplicabilidad futura según lo conocido antes.

## 6. Implementación real
src/temporal.py valida campos, rangos no vacíos y version_id global único. Bitemporal conserva filas que contienen valid_on y known_on en sus respectivos intervalos. Una fila elegible devuelve evidencia; cero devuelve not_found; varias devuelve ambiguous y ninguna cita. No se oculta un conflicto eligiendo el mayor identificador.

Baseline latest ignora ambos ejes y elige mayor known_from/version_id. Baseline valid_only filtra aplicabilidad, pero ignora tanto el inicio como el cierre del registro/conocimiento y elige el más reciente. Ambas políticas reciben el mismo corpus y consultas. El coste de devolver menos citas se reporta junto al error.

La cita incluye la versión inmutable completa y SHA256 del JSON canónico de su payload. integrity_ok detecta cambios frente a la huella original; no autentica la fuente ni prueba veracidad, entailment o que las fechas estén bien registradas. Un atacante que recompute la huella no queda impedido por este control.

Complejidad O(N) de validación/filtrado, más O(K log K) de ordenación de IDs candidatos para reporte; memoria O(N+K) para listas/conjunto. No índice temporal, DB, ranking de similitud o motor GraphRAG.

## 7. Tests y benchmark ejecutados
Nueve tests pasan: 56 resultados de fixtures, fronteras exclusivas de ambos relojes, control negativo de evidencia futura, conflicto sin cita, 100 permutaciones aleatorias de orden de entrada, huella de payload cambiado, rangos/fechas/IDs inválidos y claves/modos desconocidos. Comando `python -m unittest discover -s tests -v`. Ruff y mypy del núcleo pasan. Cobertura de líneas no medida; C++/sanitizers no aplican.

Benchmark de 168 consultas, sin bucle largo, conserva entradas completas y etiquetas esperadas JSON, raw.csv y summary.json. Cada fila registra tiempo y asignaciones Python con tracemalloc, excluyendo construcción de corpus/notebook. Se mide el gate pequeño, no latencia de recuperación/LLM ni rendimiento de DB.

Notebook de cuatro celdas ejecutado secuencialmente vía IPython in-process y validado con nbformat. Incluye una consulta viva además de outputs del benchmark. No se afirma validación de kernel aislado. Figura SVG renderizada con sharp e inspeccionada: legible, sin recortes. Revisor independiente reprodujo pipeline con exit 0 y nueve tests; revisión de núcleo separada antes de cerrar PR.

## 8. Resultados con números y figura

| Política | Citas devueltas / 56 | Citas definitivas incorrectas | Fugas de conocimiento futuro | Violaciones de validez |
|---|---:|---:|---:|---:|
| latest | 56 | 48 | 24 | 32 |
| valid_only | 56 | 40 | 24 | 0 |
| bitemporal | 32 | 0 | 0 | 0 |

Bitemporal además devuelve 16 not_found y ocho ambiguous. Los 56 estados/versiones coinciden con el contrato esperado, pero esas 24 no-respuestas no son respuestas factuales acertadas. Entre 32 citas devueltas no hay versión incorrecta en estas fixtures. No se presenta 100% de precisión de un RAG general.

Valid_only tiene 32 violaciones del intervalo de conocimiento: 24 por usar filas aún no registradas y ocho por usar un registro ya reemplazado en la consulta de expiración. Su ausencia de violaciones de validez no evita look-ahead. Latest falla también por aplicar a enero una fila cuya vigencia empieza en febrero.

results/temporal.svg separa citas erróneas y ausencia de cita. Tiempos iniciales locales aproximados ~0,58–0,61 ms por consulta y pico trazado ~1,8–1,9 KB; son perfiles de un corpus de tres/cuatro filas con instrumentación, no benchmark de escala ni comparación de velocidad concluyente. La última reproducción en summary.json es la autoridad de recursos. No se infieren intervalos de confianza de una suite determinista.

## 9. Análisis crítico y ablaciones negativas
El baseline valid_only mejora un eje, pero sigue introduciendo correcciones futuras en preguntas históricas. Latest confunde “último registrado” con “aplicable”. Las consultas en fronteras muestran por qué ambos intervalos deben ser semiabiertos para no devolver dos estados en un cambio correcto.

La negativa ante solapamiento es conservadora: se devuelve ambiguous incluso si textos coinciden, porque el contrato no define fusión ni jerarquías. Una solución que negara todo tendría cero citas erróneas, pero fallaría las 32 respuestas requeridas; por eso se informa cantidad de citas y el test exige esas respuestas.

La verdad depende de metadata confiable. Un corpus con fechas falsas puede devolver evidencia incorrecta aunque el filtro sea exacto. No se evalúan consultas semánticas difíciles, recuperación de documentos relevantes ni alucinaciones del generador. Los métodos temporales ya son conocidos; este ciclo demuestra una brecha concreta de integración.

## 10. Limitaciones y madurez
Sólo consulta por clave exacta, granularidad de día y rectángulos temporales ya persistidos. Sin ingesta append-only, firmas, autenticación de fuentes, DB, horas/zonas, incertidumbre de fecha, jerarquía normativa, resolución de contradicciones sustantivas, LLM ni datos reales. No interpreta normativa ni produce consejo legal/financiero.

El host reinició scratch; se reconstruyó worktree desde GitHub y se instaló un venv local aislado con requisitos fijados (nbformat 5.10.4/IPython 9.6.0, más herramientas de desarrollo). No se dependió de archivos anteriores desaparecidos. La publicación conserva código y evidencia en GitHub.

Componente S1→S2 ejecutado, candidato M2 local sujeto a revisión técnica; propuesta GraphRAG amplia sigue parcial y no operacional. No se equiparan fechas sintéticas correctas con validación empírica o producción.

## 11. Cómo correr
Desde `05-artificial-intelligence-and-computational-systems/06-knowledge-engineering-and-rag/01-temporal-regulatory-graphrag/mvp-bitemporal-evidence-gate`:

`bash run.sh`

Python 3.12 + pip; instala herramientas notebook fijadas, ejecuta tests, experimento y notebook. Núcleo sólo biblioteca estándar. Entorno preparado del ciclo: `PYTHON=/workspace/scratch/6c8b818bd733/ia28-env/bin/python SKIP_INSTALL=1 bash run.sh`. Los cálculos no usan red/API; pip sí requiere paquetes disponibles.

## 12. Referencias BibTeX
Cinco fuentes reales verificadas en referencias.bib: Snodgrass 2000, PostgreSQL 18 rangos, Microsoft temporal tables, Lewis et al. 2020 y W3C PROV-DM 2013. Registro con fecha 28-10-2026 y límites en results/references_verified.json. No se afirman implementaciones completas de esos sistemas.

## 13. Rúbrica 1–5
Novedad 2 (gate de mecanismos temporales conocidos), rigor 4 (dos relojes, controles negativos, límites exactos), reproducibilidad 4 (inputs/etiquetas/outputs, notebook in-process), código 4 (núcleo tipado y nueve tests), claridad 4, impacto 3 (evita look-ahead de metadata, sin retrieval real), honestidad 5, MVP 4 (ejecutable acotado completo). Autoevaluación, no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: versionar la ingesta antes de conectar el filtro a recuperación semántica.

1. 06-knowledge-engineering-and-rag/01-temporal-regulatory-graphrag: añadir ledger append-only y separar fecha de fuente de registro local, con pruebas de correcciones parciales.
2. 06-knowledge-engineering-and-rag/02-retrieval-evidence-auditor: integrar ranking real después del gate y medir relevancia/cobertura temporal por separado.
3. 08-ai-reliability-security-and-governance/02-ml-governance-evidence-ledger: verificar firma/procedencia de metadata; no tratar una huella de contenido como autenticación.
