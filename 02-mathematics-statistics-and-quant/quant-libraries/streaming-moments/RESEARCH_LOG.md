# Programa acumulativo: momentos reproducibles

|Fecha|Pregunta/decisión|Evidencia durable|Negativo aprendido|Madurez|
|---|---|---|---|---|
|2026-10-29|¿Evitar cancelación por offset y fusionar?|PR101; src/moments.py, notebook.ipynb, results/raw.csv|NumPy exacto en fixtures; a1e16 datosya redondeados; extremos finitospuedenoverflow|Prototipo verificado local|
|2026-10-30|¿SD representable cuando varianza no cabe?|src/scaled.py; notebook_scale.ipynb; results/scale_raw.csv; PR enlazado en entrega|Escala mala rechazada; NumPy+mismaescala más preciso/rápido; no recuperar señalperdida|Prototipo acumulativo, no operacional|

## Selección de tres ideas30
1 Pesos arbitrarios: útil pero exige definir ddof/semántica; aplazar para no diluir cierre.
2 Sólo RSS/timing: mejora evidencia29 pero no cierra overflow; incorporar5repeticiones y memoria separada como apoyo.
3 Unidad binaria externa y estados explícitos: elegida; cierra brecha29 sin nueva carpeta ni contrato compartido global.

## Roadmap con gates
1 src/scaled.py: escala dinámica y merge entre escalas sólo tras prueba de invariantes y pérdida informativa; mantener rechazo mixto como control.
2 src/benchmark_scale.py: ordenes/distribuciones y límites subnormales; gate falsable: ningún éxito con SD0 si oráculoSD>0representable.
3 config_scale.json/results: repeticiones30+,RSS de procesos separados y distribución de timings antes de presupuesto de rendimiento. No prometido/ejecutado todavía.

Continuar adaptador explícito; ajustar ante normalization_failure; cerrar afirmación de superioridad universal. No ascenso de programasadvanced-research, sin equivalencia automáticaS2/M2. Nuevo lenguaje no justificado: núcleo simplePython; cross-tests EL83 existentes se conservan sin cambios.

##31oct2026: pregunta y contribución
¿Podemos seleccionar escala sin inspección futura preservando SD representable? Elegida autoescala frente a merge/ponderación (comparación en informe_dynamic.md punto4). Mapa:29cancelación→30rango externo→31rango online/subnormal. Hipótesis45fixtures≤1e−12aprobada; negativos de redondeo y NumPy más rápido conservados. Derivación original/propuesta/propiedades: derivacion_dynamic.md. Adaptación de ingeniería conocida, no contribución científica original.
Decisión: continuar; no reemplazar implementación30ni declarar superioridad. Próximo hito src/dynamic.py merge entre escalas con contrato y pruebas contra Decimal; segundo src/benchmark_dynamic.py órdenes y nmayores antes presupuesto productivo; tercero compensación de pérdida bajo reescalado con coste explícito. Todo pendiente, sin inflar madurez.

##1nov2026: conectar resúmenes, no crear otro programa
Tresideas: pesos/compensación/fusiónautoescalas (informe_merge.md4). Elegida fusión porque cierra hito31 y habilita módulos conectables. Contribuciónclasificada adaptacióningeniería/auditoría. FórmulaoriginalChan→rebase→Chan; derivaciónypropiedadesen derivacion_merge.md. Hipótesis48escenarioserrorSD≤max(4ulp,1e−12relativo)cumplida; conteosconservados. Negativos: NumPy má rápido, árbolnoasociativobitabit, pérdidadecomponentesextremos, mergeonly no es costefull.
Hitos: [cerrado1nov] merge dinámico contrafixtures/oráculo; [pendiente] contratoexportación ycrosslanguage numérico con tolerancias justificadasantesdeAPI pública; [pendiente]n/distribuciones/órdenesadversosmayores antesvalidaciónexterna; [pendiente] compensaciónsólotrasbenchmark error/coste. Noascensodelprograma aoperacional. Decisióncontinuar, ajustarcuando diagnosticapérdida, cerrarafirmaciónsuperioridaduniversal.

##2nov2026 — conectar productores y consumidor real
Tres ideas: pesos, compensación, transporte/consumidorC++ (informe_transport.md4). Elegida tercera: cierra hito de exportación1nov sin abrir otra carpeta. Mapa: momentos→escala→autoescala→fusión→interoperabilidad. Hipótesis: campos exactos, SDdiscrepancia≤max(4ulp,1e−12rel), reducción debytes>10para n1024. Cumplida en24escenarios;72filas; C++no aporta fórmula nueva. Negativos conservados: IPC más lento, historial de diagnósticos omitido, validación sólo estructural.
Hitos: [cerrado2nov] contratoMOMENTS_V1/consumidorC++20/CMakeCTest/ASanUBSan y fixturescruzadas; [pendiente] lotes/persistencia con presupuesto justo; [pendiente]V2diagnósticos/procedencia y compatibilidad; [pendiente]segundo toolchain/arquitectura antes de uso externo. Continuar integración; ajustar semántica de pérdida; cerrar afirmación de superioridad temporal. Prototipo verificado local, no operacional ni contribución científica original.
