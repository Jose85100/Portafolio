# CICLO_DIARIO IA — 24 de octubre de 2026

## 1. Título
Outbox y recibos semánticos en dos almacenes independientes ante pérdida de ACK.

## 2. Hipótesis y novedad incremental
Hipótesis fijada en config.json: key_hash debe producir cero efectos duplicados/cero efectos faltantes y rechazar el100% de probes de payload cambiado, con baseline no_dedup duplicando efectos cuando se pierde ACK. key_only debe revelar una ablación negativa: deduplica pero acepta en silencio otra intención. Es un aporte incremental de implementación y auditoría al portafolio, no invención de outbox ni promesa de originalidad científica mundial.

## 3. Estado del arte con fuentes reales
Featonby, AWS Builders’ Library, explica tokens de idempotencia, retención y conflicto de parámetros con mismo token. Richardson documenta transactional outbox y publicación repetida si el relay falla después de publicar; su patrón idempotent consumer registra identidad en la transacción del consumidor. SQLite describe BEGIN/COMMIT, un escritor simultáneo y atomicidad bajo supuestos de almacenamiento. Cinco fuentes primarias verificadas el24-10-2026, URLs completas en referencias.bib y results/references_verified.json. Son documentación técnica pertinente, no cinco papers ni revisión exhaustiva. No se atribuye a estas fuentes rendimiento local medido.

## 4. Brecha identificada
La propuesta del pilar04-event-driven-ai-automation era S1 sin implementación. El MVP previo en06-fault-tolerant-ai-execution-recovery verifica efecto/checkpoint dentro de una misma SQLite. Esa atomicidad no se extiende a una API remota. Este componente separa emisor y proveedor en dos archivos SQLite/conexiones/transacciones y prueba la frontera ambigua entre commit proveedor y ACK emisor. No altera código compartido ni el MVP de checkpoints previo.

## 5. Diseño experimental y configuración
144 lotes pareados: tamaños20/100 × probabilidades de perder ACK0/.35/.8 ×8 semillas ×3políticas. Máximo8 intentos por evento. El plan de pérdidas se pregenera por semilla y es idéntico entre políticas. Efectos son enteros positivos sintéticos; no pagos ni datos de clientes. La falla se inyecta exclusivamente después del commit del proveedor y antes del ACK. Un test de integración termina el worker realmente mediante os._exit(77), mientras benchmark usa excepción después de cerrar la conexión confirmada. Otro test lanza12 llamadas concurrentes desde4threads al proveedor.

Se mide antes de probes: efectos, duplicados, confirmaciones, faltantes, intentos, wall-clock, pico de asignaciones Python tracemalloc y bytes SQLite. Después se prueba una reutilización con importe distinto por evento. Así los probes no contaminan el indicador de duplicados ni el tiempo del relay. CPU, plataforma, versiones Python/SQLite y semillas quedan en JSON. No se modelan red, broker ni costo cloud.

## 6. Implementación
src/engine.py: initialize/enqueue/apply/dispatch/metrics. Emisor registra job+outbox atómicamente. Proveedor key_hash consulta recibo bajo BEGIN IMMEDIATE y confirma recibo SHA256 del envelope canónico junto con efecto; una clave existente con digest distinto causa rollback/validación. El relay ACKea sólo después del retorno del proveedor. No hay ATTACH ni transacción que abarque ambas bases.

Invariante: con política fija, recibos conservados, claves estables/namespace y DB íntegra, cada clave tiene a lo sumo un efecto. El recibo se crea sólo junto al efecto. Inducción sobre intentos: clave nueva inserta una vez bajo lock; repetida equivalente retorna recibo; repetida distinta se rechaza. No es un teorema de terminación: presupuesto finito o indisponibilidad pueden dejar pendiente.

Baselines: no_dedup aplica cada intento; key_only retorna recibo sin comparar intención; key_hash añade comparación. El servicio implementa el contrato; no basta enviar claves a un tercero que las ignore.

## 7. Tests y benchmarks ejecutados
Nueve tests pasan: enqueue idempotente/conflicto, os._exit77 con recuperación desde disco, control negativo duplicado, conflicto semántico sin efecto adicional, ablación key_only, invariantes con25eventos y retries aleatorios, ACK repetido sin entrega,12requests concurrentes/4threads y entradas inválidas. Comando: `python -m unittest discover -s tests -v`. Ruff src/tests/benchmarks pasa. Mypy del núcleo pasa con mypy.ini local; la configuración global disparó error interno de mypy2.4 y se aisló su configuración explícitamente. No se midió cobertura de líneas. C++/sanitizers no aplican.

Comando integral reproducido con dependencias ya presentes. README incluye instalación con versiones fijadas. El notebook se ejecuta de arriba abajo con IPython in-process y outputs reales/nbformat validado; no kernel aislado. Figura SVG renderizada con sharp e inspeccionada visualmente sin clipping.

## 8. Resultados con números y figura
Promedios sobre8semillas, n=100:

| Pérdida ACK | Política | Duplicados por100jobs | Confirmados | Rechazo conflicto |
|---|---|---:|---:|---:|
| 0 | no_dedup | 0 | 100% | 0% |
| .35 | no_dedup | 58,375 | 100% | 0% |
| .35 | key_only | 0 | 100% | 0% |
| .35 | key_hash | 0 | 100% | 100% |
| .8 | no_dedup | 318,75 | 83,625% | 0% |
| .8 | key_hash | 0 | 83,625% | 100% |

Cero efectos faltantes en todos los lotes, pues la falla ocurre después de la aplicación, no antes. Cero duplicados en ambas políticas idempotentes. Esto no implica confirmación completa: con.8 hay16,375% pendientes al agotar8intentos; referencia analítica de independencia: .8^8=16,777216%. No se usa esa referencia como estimación real ni supuesto universal.

Figura results/duplicates.svg muestra.35. Tiempos iniciales locales n100/.35: no_dedup~0,624s ±SE0,066; key_only~0,470s ±SE0,018; key_hash~0,443s ±SE0,031. Son mediciones de esta corrida con orden fijo y fsync: no se concluye ventaja de latencia de hash sobre key_only. JSON se actualiza al reproducir y es autoridad para tiempos. Los bytes DB iniciales n100/.35 son51.200 baseline y61.440 idempotentes. Tracemalloc~2,4–3KB sólo cubre asignaciones Python muestreadas; excluye buffers SQLite/OS y no representa RSS total. Para escala20/100 ver JSON/CSV; no prueba capacidad operacional.

## 9. Análisis crítico y ablaciones negativas
Outbox sin dedup del receptor persiste intención pero repite efectos. key_only preserva cardinalidad pero es insuficiente para validar intención: retorna efecto anterior cuando cambia payload. key_hash detecta conflicto, pero no recupera ACK perdido sin nuevo intento exitoso. La variante sin pérdidas tiene cero duplicados incluso sin dedup, control de que la mejora no depende de contar probes como fallos. Mantener recibos consume almacenamiento; no se implementó TTL.

No se afirma que retry sea independiente en sistemas reales. Los tiempos de políticas se ejecutan en orden fijo (cache/carga confunden comparación); las secuencias de fallos sí están pareadas. No se probaron cargas masivas ni fairness de varios remitentes. La prueba concurrente cubre proveedor local y serialización SQLite, no consenso distribuido.

## 10. Limitaciones, seguridad y madurez
No energía/disco corrupto, red real, proveedor HTTP, broker, cambios de política durante vida del almacenamiento, TTL/borrado, claves entre tenants mal asignadas, orden global ni workers emisores concurrentes/fencing. La huella SHA256 es coherencia de intención, no autenticación/integridad contra un atacante con acceso a DB. Entradas no incluyen datos personales; no secretos. La validación del envelope sólo abarca version/operación/importe sintéticos; producción requeriría canonización de todos los campos relevantes y permisos.

Componente avanza de diseño S1 a S2 ejecutado; candidato M2 local condicionado a revisión independiente. No se eleva pilar entero ni se denomina operacional o validado con datos reales. Notebook IPython secuencial no certifica kernel Jupyter aislado; SVG/outputs guardados son inspeccionables.

## 11. Comando exacto
Desde la carpeta `05-artificial-intelligence-and-computational-systems/10-ai-orchestration-engineering/04-event-driven-ai-automation/mvp-outbox-idempotency`:

`bash run.sh`

Python3.12 y pip; instala requirements.txt (herramientas notebook), luego tests, benchmark y notebook. En entorno preparado: `PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" SKIP_INSTALL=1 bash run.sh`. Los cálculos no necesitan red ni servicios externos; pip sí necesita paquetes disponibles.

## 12. Referencias BibTeX
Cinco entradas en referencias.bib con URL primaria verificada. No se inventan DOI ni fechas de publicación para documentación viva; la fecha de acceso es24-10-2026. Registro de verificación en results/references_verified.json.

## 13. Rúbrica1–5
Novedad2 (patrones establecidos integrados y refutados localmente), rigor4 (dos almacenes, fronteras claras, procesos/concurrencia), reproducibilidad4 (semillas y outputs; runtime no aislado), código4, claridad4, impacto3 (evita clase concreta de fallo sin red real), honestidad5, MVP4 (completo acotado, no sistema operacional). Autoevaluación, no certificación independiente.

## 14. Siguiente iteración
Siguiente iteración recomendada: falsificar el contrato al caducar recibos y recibir reintentos tardíos.

1. 10-ai-orchestration-engineering/04-event-driven-ai-automation/mvp-outbox-idempotency: implementar TTL y demostrar duplicado tras expiración con replay tardío.
2. 10-ai-orchestration-engineering/06-fault-tolerant-ai-execution-recovery: añadir leases y fencing para workers emisores concurrentes.
3. 08-ai-reliability-security-and-governance: formalizar namespace/autorización y mínimos de auditoría de recibos sin payload sensible.
