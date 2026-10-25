# CICLO_DIARIO IA — 25 de octubre de 2026

## 1. Título
Auditor exacto acotado de conformidad de trazas cuando timestamps empatados no revelan el orden.

## 2. Hipótesis, tres ideas y novedad incremental
Se compararon tres ideas antes de implementar:

| Idea | Decisión | Razón |
|---|---|---|
| Bounds de conformidad bajo orden parcial | Elegida | Rota a pilar07, propuestaS1 sin código, falsificación pequeña y exacta |
| TTL y replay de recibos outbox | Diferida | Repetiría pilar10 del24oct; requiere otra familia de fallos |
| Monitoreo probabilístico de drift | Diferida | Próxima a conformal del23oct; menor diversidad en este ciclo |

Hipótesis en config.json: bounds produce cero veredictos definitivos erróneos y decide al menos50% en dataset equilibrado; desempate arbitrario y optimista superan10% de error. El aporte es una adaptación computacional acotada y un gate de incertidumbre/recursos para el portafolio; **los bounds de conformidad incierta ya existen en literatura**, no se reivindica algoritmo nuevo ni prioridad mundial.

## 3. Estado del arte con cinco referencias verificadas
Pegoraro, Uysal y van der Aalst, Conformance Checking over Uncertain Event Data (arXiv2009.14452), estudian bounds de conformidad al alinear trazas inciertas. Pegoraro y van der Aalst, Mining Uncertain Event Data in Process Mining (1910.00089), introduce taxonomía e incertidumbre explícita. Pegoraro, Probabilistic and Non-Deterministic Event Data… (2205.04827), revisa el área. Pegoraro, Uysal y van der Aalst, Discovering Process Models from Uncertain Event Data (1909.11567), preserva incertidumbre en descubrimiento. El Process Mining Manifesto de IEEE Task Force (página oficial, publicación2012) encuadra estándares y desafíos.

Se abrieron páginas primarias arXiv verificando título/autores/identificador/resumen y página oficial del manifesto. La URL sinwww del manifesto falló502; www funcionó. No revisión exhaustiva ni replicación de esos trabajos. Primeros dos trabajos se solapan y no son evidencias independientes. BibTeX usa años de preprint explícitos, no mezcla2020 con publicación editorial2021 del primero. URLs y registro en referencias.bib/results/references_verified.json.

## 4. Brecha en repositorio
main inspeccionado98659cc, sin PR abiertos al inicio. El pilar07/01-process-mining-risk-operations era propuestaS0/S1 de conformance/logs sin implementación. Los aportes anteriores eran conformal en pilar02 y recibos outbox en10. Este auditor cambia de problema: no prediceY, no envía efectos ni deduplica mensajes; identifica qué conclusiones de orden son justificables por un log con timestamps empatados.

## 5. Diseño experimental y configuración
Referencia única con4/8/12actividades distintas. Ocho semillas,10casos por escenario/longitud/semilla, cinco escenarios equilibrados: ordered_valid, ordered_invalid (intercambio real de dos actividades sin empate), tied_valid, tied_invalid (intercambio oculto por empate) y missing_invalid (actividad ausente).1.200trazas; tres políticas sobre los mismos buckets;3.600comparaciones CSV. El orden latente sólo se guarda para evaluar; el auditor recibe buckets y referencia sin verdad latente. No entrenamiento, selección supervisada ni partición que pueda filtrar etiquetas.

Entre buckets el orden es conocido; dentro todos los órdenes son admisibles. No se representan intervalos de timestamp solapados generales ni causalidad. La corrupción que cambiara el orden entre buckets invalida el supuesto de que la realización verdadera esté en el conjunto. Datos sintéticos con semilla fija y nombresstage_XX; sin clientes ni información personal. event_logs.jsonl conserva entradas y verdad de evaluación.

## 6. Implementación real y matemática
src/conformance.py implementa coste de inserción/eliminación (1cada operación; sustitución equivale a2), vía programación dinámica. Lenguaje normativo es una única secuencia finita, no red de Petri/BPMN ni concurrencia legítima del proceso. Para realizaciones admisiblesL(b), se calcula L=min d(s,m) y U=max d(s,m). Veredicto conformant siU=0; nonconformant siL>0; ambiguous siL=0<U.

Soundness dentro del modelo: si la realización verdadera pertenece aL(b), su coste está entreL yU por definición de extremos enumerados. Esto no identifica qué orden ocurrió. Coste por realización O(N·M), memoria de distancia O(M). EnumeraciónK realizaciones requiere O(KNM) y almacena listas de permutaciones/costes. Es factorial: producto factorial de tamaños de bucket, máximo720candidatos y32eventos. Con etiquetas repetidas se usa bound factorial conservador; un rechazo puede ocurrir aun si había pocas secuencias únicas. Se calcula bound completo antes de decidir; si excede no se enumera ni se devuelven cotas ficticias: lower/upperNone y budget_exceeded.

Baseline arbitrary conserva orden de llegada dentro del empate. Baseline optimistic usa sóloL y devuelve conformidad cuando existe un orden válido, aun si otro es inválido. Ambos reciben mismos datos y usan mismo coste para que el contraste sea semántico, no por scoring distinto.

## 7. Tests y benchmarks reales
10tests pasan: traza exacta, empate ambiguo y control arbitrario, evento faltante, traza vacía, guardia de720 (incluyendo producto de varios buckets), repetición de labels, invariancia a permutación de empate,100casos aleatorios de extremos contra enumeración independiente,100propiedades simetría/límite de distancia y entradas inválidas. Comando `python -m unittest discover -s tests -v`. Ruff en src/tests/benchmarks pasa; mypy en núcleo pasa con configuración local. Cobertura de líneas no medida; C++/sanitizers no aplican.

Benchmark guarda todas las entradas y comparaciones más resumen18filas y escala para anchuras1–7, cinco repeticiones por anchura. Perfil wall-clock con tracemalloc; mide asignaciones Python, no memoria nativa/RSS ni carga de un servicio. Arbitrary se cronometra sin tracemalloc y optimistic reutiliza cómputo de bounds: **no es comparación justa de latencia entre métodos** ni se usa como claim de velocidad. Escala de bounds sí usa mismo esquema. Hardware/CPU/plataforma/Python registrados en JSON.

Notebook de cuatro celdas ejecutado secuencialmente por IPython in-process, outputs reales y nbformat validado; no se afirma kernel Jupyter aislado. FiguraSVG renderizada con sharp a PNG e inspeccionada: legible/sinclipping. Revisor independiente reprodujo comando integral exit0 y no encontró bloqueantes.

## 8. Resultados numéricos y figura

| Política | Errores definitivos /1.200trazas | Tasa error total | Decisiones | Abstenciones |
|---|---:|---:|---:|---:|
| Arbitrary | 252 |21%|1.200(100%)|0|
| Optimistic |240|20%|1.200(100%)|0|
| Bounds |0|0%|720(60%)|480(40%)|

Hipótesis satisfecha en diseño sintético. El error entre decisiones de bounds también es0, pero480abstenciones **no se cuentan como aciertos**. Las tasas están determinadas por mezcla equilibrada de escenarios, no prevalencia operativa. Error arbitrary por semilla:16/18/18/24/24/22/18/28%; media21%, SEentre8semillas~1,464puntos. Approx ±1,96SE no sería intervalo válido de desempeño operacional: mezcla y verdad se fijaron artificialmente. Optimistic y bounds tienen error idéntico entre semillas por construcción; SE0 no significa incertidumbre externa nula.

Escala inicial bounds: anchura6 enumera720órdenes en~0,045s con picoPython~146KB; anchura7 exige5.040candidatos y retorna budget_exceeded sin evaluación. Los valores temporales se regeneran al reproducir: summary.json es autoridad para recursos actuales. Figura results/verdicts.svg diferencia errores rojos de abstenciones azules, no presenta abstención como exactitud.

## 9. Análisis crítico y ablaciones negativas
Tied_valid y tied_invalid admiten los mismos órdenes observables: aceptar siempre mínimo oculta incumplimientos; seleccionar un desempate arbitrario inventa certeza y causa falsos positivos/negativos. Bounds elimina esas afirmaciones injustificadas mediante abstención, no recuperando el orden perdido. Missing_invalid sigue siendo desviación segura: ninguna permutación crea un evento ausente. Ordered_valid/invalid sirven de controles sin empate.

La hipótesis es deliberadamente local y la soundness se desprende del conjunto de órdenes completo; no equivale a generalización estadística. Un modelo mal especificado o reloj con skew puede producir un veredicto incorrecto respecto al proceso real aunque cálculo sea exacto. El límite factorial es una falla explícita de escalabilidad del enumerador; no se oculta tras muestreo.

## 10. Limitaciones, riesgos y madurez
Sólo referencia secuencial y buckets ya normalizados. No logs abiertos empíricos/XES, resolución de reloj estimada, netos de proceso con loops/concurrencia, incertidumbre de etiqueta/identidad/caso, probabilidad sobre órdenes, reparación de eventos ni atribución causal de cuellos de botella. El programa amplio pedía datos públicos y comparación con sistemas generales: siguen pendientes. No herramienta regulatoria ni detector de fraude.

Datos sin información personal; el gate32/720 controla explosión combinatoria de entrada. Sin interfazred, auth, permisos, monitoreo ni despliegue. Para producción requiere modelo de amenaza de logs alterados y fuentes de tiempo confiables. Componente pasaS1→S2ejecutado; revisión técnica local no valida un dominio entero ni operación real. MadurezM2candidata local, no operacional.

## 11. Cómo correrlo
Desde `05-artificial-intelligence-and-computational-systems/07-intelligent-automation-and-process-mining/01-process-mining-risk-operations/mvp-partial-order-conformance`:

`bash run.sh`

RequierePython3.12+pip; instala requirements.txt fijado para notebook. Núcleo sólo bibliotecaestándar. Entorno preparado: `PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" SKIP_INSTALL=1 bash run.sh`. Calcula sin red/API; pip sí necesita paquetes disponibles.

## 12. Referencias BibTeX
Cinco entradas verificadas en referencias.bib: arXiv2009.14452,1910.00089,2205.04827,1909.11567 y Process Mining Manifesto oficial. DOIarXiv para los preprints, URLprimaria para manifesto. Registro con fecha25-10-2026. La doc oficial itertools también se consultó para semántica de enumeración; no se presenta como investigación original.

## 13. Rúbrica1–5
Novedad2 (adaptación de bounds conocidos), rigor4 (extremos exactos, límites explícitos, controles y revisión), reproducibilidad4 (inputs/semillas/outputs, notebook in-process), código4 (núcleo tipado y10tests), claridad4, impacto3 (evita auditorías de orden injustificadas, sin datos reales), honestidad5, MVP4 (completo acotado, kernel aislado/validezempírica pendientes). Autoevaluación, no certificación independiente.

## 14. Siguiente iteración
Siguiente iteración recomendada: evaluar resolución de timestamps y variantes de referencia con logs públicos sin esconder los casos ambiguos.

1. 07-intelligent-automation-and-process-mining/01-process-mining-risk-operations: incorporar log abierto con licencia y metadatos de resolución, preservar incertidumbre/clockskew.
2. 07-intelligent-automation-and-process-mining/02-verifiable-workflow-orchestration: extender lenguaje a varias secuencias o autómata y comparar con enumerador exacto en instancias pequeñas.
3. 08-ai-reliability-security-and-governance: definir gate de no-decisión y trazabilidad de qué evidencia adicional elimina una ambigüedad.
