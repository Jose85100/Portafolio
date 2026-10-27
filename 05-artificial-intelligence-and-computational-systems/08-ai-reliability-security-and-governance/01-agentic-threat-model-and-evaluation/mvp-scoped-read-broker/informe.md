# CICLO_DIARIO IA — 27 de octubre de 2026

## 1. Título
Broker read-only para agentes: autoridad anclada a un descriptor y evaluación de fallos TOCTOU.

## 2. Tres ideas, hipótesis y novedad incremental

| Idea | Decisión | Motivo |
|---|---|---|
| Broker read-only y auditoría determinista de TOCTOU | Elegida | Nuevo componente de seguridad del pilar 08, propuesta S1 y prueba pequeña verificable |
| Reevaluación holdout de jueces LLM | Diferida | Ya existe llm-evaluation-judge-reliability; menor diversidad del ciclo |
| Memoria con TTL y replay | Diferida | Próxima al trabajo de outbox del 24 de octubre |

Hipótesis fijada en config.json: el broker anclado no devuelve el canario exterior en siete escenarios de escape; resolver antes de abrir falla en los dos interleavings inyectados; el coste de utilidad del broker anclado se limita al alias interno symlink de la suite. El aporte es una integración defensiva auditada para tool calls, no una nueva primitiva de seguridad ni un método que resuelva prompt injection.

## 3. Estado del arte y cinco fuentes verificadas
OWASP recomienda mantener autorización y mínimo privilegio fuera del modelo; se aplica a la frontera del tool, sin evaluar el modelo mismo. MITRE CWE-367 caracteriza la diferencia temporal entre comprobar una propiedad y usar el recurso. La documentación Python 3.12 describe os.open/dir_fd y sus límites de portabilidad. Linux open(2) documenta descriptores, O_NOFOLLOW y apertura relativa; path_resolution(7) explica componentes, rutas relativas y symlinks.

Se abrieron las cinco páginas primarias y se verificaron títulos y secciones relevantes. referencias.bib guarda URLs reales y fecha de acceso; results/references_verified.json registra alcance. Es prior art de ingeniería y estándares documentales, no cinco papers ni revisión exhaustiva. No se inventan DOI, certificaciones ni referencias.

## 4. Brecha del repositorio y revisión inicial
main inspeccionado e0cb173, con PR #88 de economía, #87 de riesgo y #84 de matemáticas abiertos; ninguna ruta de este proyecto se solapa. La propuesta 08-ai-reliability-security-and-governance/01-agentic-threat-model-and-evaluation estaba S0/S1 sin motor. El pilar ya tiene evaluación de jueces, pero no se encontró un broker con recorrido por descriptores y pruebas TOCTOU. No se modifican shared/contracts ni los aportes conformal, outbox, process mining u OPE de ciclos previos.

Se reduce la propuesta amplia a un único tool de lectura en filesystem Unix. Autorización multi-tenant, sandbox general, evaluación de LLMs y despliegue siguen pendientes. No se presenta el programa entero como implementado.

## 5. Diseño experimental y modelo de amenaza
12 escenarios × ocho variantes de nombres/contenido × tres políticas = 288 solicitudes, 96 por política. Siete escenarios de intento de escape: traversal, sibling con prefijo coincidente, symlink de archivo, symlink de directorio, sustitución de padre, sustitución de hoja y hardlink estático al canario. Tres solicitudes de utilidad: archivo directo, archivo nested y alias symlink interno benigno. Dos casos inválidos: tool distinto y presupuesto mayor al grant.

Cada solicitud usa un TemporaryDirectory nuevo que contiene raíz autorizada y archivos exteriores de prueba. El canario exterior es sintético y pertenece a esa misma fixture temporal; no se prueba sobre archivos de usuario ni secretos reales. No red, shell ni LLM. Los tres métodos reciben la misma clase de solicitud, grant y semilla; se reconstruye filesystem nuevo para que una mutación de un método no contamine al siguiente.

La mutación TOCTOU es un hook determinista de backend, no una carrera concurrente aleatoria: después del check o adquisición del descriptor padre, renombra/sustituye un objeto por un symlink controlado. El hook no es parte del payload y no puede enviarlo el agente. Las ocho repeticiones varían nombres/contenido; no son ocho ataques naturales independientes ni permiten inferir una tasa general de evasión.

## 6. Implementación y contrato de autoridad
src/broker.py acepta exactamente tool/path/max_bytes. Sólo read_text, path string no vacío y sin NUL, entero real para presupuesto (no bool), máximo confiable por grant de 4.096 bytes. Configuración root y cap sólo la proporciona el proceso confiable. El payload no puede ampliar autoridad con campos approval, grant u otro tool. Se asume objeto JSON ya parseado, no objetos Python arbitrarios ni unpickle.

El broker abre un descriptor de directorio en el grant. En modo anchored_fd exige ruta relativa con componentes limpios, máximo 16 y 256 caracteres; duplica descriptor raíz, abre cada padre relativo con O_DIRECTORY/O_NOFOLLOW y la hoja con O_NOFOLLOW/O_NONBLOCK. fstat permite sólo archivo regular y nlink=1; el control de hardlinks es estático, no una prueba contra todas las carreras de enlaces. El contenido debe ser UTF-8.

max_bytes limita una respuesta aceptada: se inspeccionan hasta max_bytes+1 bytes para detectar y rechazar una lectura demasiado grande. No se devuelve truncamiento como si fuera el archivo completo. O_NONBLOCK y fstat evitan que un FIFO bloquee el proceso. Descriptores temporales se cierran en finally, incluso tras una negativa. El broker no tiene llamadas de escritura; las mutaciones pertenecen exclusivamente al generador de pruebas.

Semántica del grant: descriptor autoriza el objeto de directorio abierto. Si un padre ya abierto se renombra, el descriptor conserva su objeto original; por eso race_parent devuelve el contenido público original en lugar de seguir el nuevo symlink. No se demuestra que el pathname actual del objeto siga estando bajo la raíz textual. No es un aislamiento completo del namespace del sistema operativo.

Complejidad por solicitud: O(d+b) para profundidad d≤16 y hasta b+1 bytes inspeccionados, memoria O(b). No protege contra mounts hostiles, kernel, carreras de creación/eliminación de hardlinks, contenido modificado por un adversario, raíz de grant maliciosa o uso concurrente de close/read y reciclado de descriptores. Ciclo de vida del broker tiene propietario único en este MVP.

## 7. Tests y benchmarks ejecutados
10 tests pasan: suite de no escape en todas las fixtures; control negativo de ambos interleavings en resolve_then_open; traversal contra prefijo; conservación del objeto del padre abierto; coste de alias interno; esquema exacto y bool/extra campos; tamaño y UTF-8; FIFO no bloqueante; 100 negativas sin fuga observable de descriptores en /proc/self/fd; broker cerrado e idempotencia de close. Comando `python -m unittest discover -s tests -v`. Ruff en src/tests/benchmarks y mypy del núcleo pasan. Cobertura de líneas no medida. C++/sanitizers no aplican.

Benchmark conserva raw.csv con escenario, semilla, permiso/negativa, canario/safe flags, motivo y recursos, sin contenidos leídos ni paths temporales absolutos. JSON registra configuración, plataforma, CPU y versiones. Figura SVG renderizada a PNG con sharp e inspeccionada sin recortes. Notebook ejecutado de arriba abajo, cuatro celdas con outputs reales mediante IPython in-process; no se afirma kernel aislado.

Revisor independiente reprodujo comando integral con exit 0, 10 tests y notebook; leyó núcleo y no identificó bloqueantes en el alcance declarado. Esa revisión local no equivale a prueba formal de seguridad general.

## 8. Resultados numéricos y figura

| Política | Canario exterior / 56 intentos | Tasa en fixtures | Lecturas benignas / 24 | Pérdida de utilidad |
|---|---:|---:|---:|---:|
| prefix | 56 | 100% | 24 | 0% |
| resolve_then_open | 24 | 42,857% | 24 | 0% |
| anchored_fd | 0 | 0% | 16 | 33,333% |

El baseline avanzado resuelve ataques estáticos con symlinks/traversal, pero falla en ocho repeticiones de race_parent, ocho de race_leaf y ocho del hardlink estático. El broker anclado lee safe en race_parent y niega race_leaf; no se exige que toda solicitud adversarial produzca negativa, sino que nunca devuelva el recurso canario. Su rechazo de todos los symlinks también niega ocho aliases internos deseados. La pérdida de utilidad es respecto al flujo benigno deseado, no un error de su política explícita sin symlinks.

Las solicitudes de tool distinto y presupuesto excesivo se niegan por esquema en las tres políticas. No se evalúa una política que niega todo como supuesto éxito; se comprueban los archivos directos/nested permitidos.

results/authority.svg separa lecturas de canario y negativas benignas. Tiempo inicial medio local aproximado: 67 μs prefix, 210 μs resolve_then_open y 49 μs anchored_fd; pico tracemalloc ~5 KB por solicitud. Son medias de una mezcla de casos con trayectorias de denegación distintas y con instrumentación. No se concluye que el broker anclado sea más rápido en producción ni se compara latencia LLM. JSON de la última reproducción es autoridad para tiempos. Tracemalloc no incluye toda la memoria nativa del OS y no es RSS del servicio.

## 9. Análisis crítico y ablaciones negativas
Comparar strings con startswith no expresa pertenencia de recurso al grant; '..' y nombres hermanos con el mismo prefijo lo falsifican. Resolver el pathname antes de abrir mejora el caso estático, pero el estado puede cambiar entre ambas acciones. La prueba TOCTOU fuerza esa intercalación y evita concluir seguridad sólo porque una carrera casual no ocurrió.

El control de descriptores cambia la unidad de autoridad al objeto ya abierto, y la negativa a seguir links reduce caminos ambiguos; no valida contenido de documentos ni instrucciones de un LLM. El chequeo de nlink demuestra un caso estático, no resuelve adversarios capaces de modificar enlaces durante la operación. La pérdida de alias interno es una ablación de utilidad necesaria: el resultado no es “cero escapes y cero coste”.

Las proporciones dependen de la selección equilibrada de fixtures; no tienen significado probabilístico para ataques externos. No se ajustaron casos tras resultados para ocultar fallos de utilidad. Casos reales adicionales podrían romper el alcance: el informe y MVP delimitan exclusiones antes de cualquier despliegue.

## 10. Limitaciones, seguridad y madurez
Linux/Unix con dir_fd, O_NOFOLLOW y /proc/self/fd para un test; no se declara portabilidad Windows. El grant debe ser confiable y la vida del broker monohilo/propietario único. No autenticación multi-tenant, mounts o kernel hostiles, reparación de contenido, extracción de secretos, writes/red, adversario con código Python en el mismo proceso ni resistencia general a prompt injection. Los dos baselines son controles negativos deliberadamente inseguros, no opciones sugeridas para uso real.

La suite usa archivos propios de prueba. No necesita datos sensibles y no registra payload de archivos. Las fuentes OWASP recomiendan una frontera de autorización externa al modelo; implementar este caso concreto no certifica las demás capas.

Componente S1→S2 ejecutado, candidato M2 local con revisión técnica independiente; el programa completo sigue parcial y no operacional. No se confunde el notebook ejecutado in-process con validación de kernel aislado.

## 11. Comando exacto
Desde `05-artificial-intelligence-and-computational-systems/08-ai-reliability-security-and-governance/01-agentic-threat-model-and-evaluation/mvp-scoped-read-broker`:

`bash run.sh`

Linux/Python 3.12 + pip. Instala herramientas notebook fijadas, prueba, ejecuta benchmark y notebook. Núcleo sólo biblioteca estándar. Entorno preparado: `PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" SKIP_INSTALL=1 bash run.sh`. Los cálculos no requieren API/red; pip sí necesita paquetes disponibles.

## 12. Referencias BibTeX
Cinco entradas reales con URLs primarias verificadas y fecha 27-10-2026 en referencias.bib; registro en results/references_verified.json. OWASP, MITRE CWE-367, documentación Python os y manuales Linux open/path_resolution. No se inventan años de publicación de documentación viva, DOI o cinco papers inexistentes.

## 13. Rúbrica 1–5
Novedad 2 (adaptación de mecanismos conocidos a un tool broker evaluado), rigor 4 (controles negativos e interleavings deterministas), reproducibilidad 4 (fixtures/outputs y notebook in-process), código 4 (núcleo tipado y diez tests), claridad 4, impacto 3 (frontera concreta, no sistema general), honestidad 5, MVP 4 (ejecutable completo acotado). Autoevaluación, no auditoría de certificación.

## 14. Siguiente iteración
Siguiente iteración recomendada: comparar mecanismos de resolución del OS y ampliar el modelo de amenaza sin convertir resultados de fixtures en garantías universales.

1. 08-ai-reliability-security-and-governance/01-agentic-threat-model-and-evaluation: comparar openat2 y políticas explícitas de mounts/links con más interleavings y pruebas Linux aisladas.
2. 10-ai-orchestration-engineering/07-orchestration-observability-governance: añadir identidad de principal, grants versionados y auditoría de decisiones sin contenido sensible.
3. 04-agentic-ai-and-multi-agent-systems/01-evidence-grounded-research-agents: integrar el broker en un agente de prueba y medir propuestas indebidas, denegaciones y utilidad por separado.
