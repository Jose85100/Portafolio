# Incremento 3-nov-2026 — envelope de auditoría de momentos

## 1. Título y pregunta

**Envelope lateral con estado explícito de diagnósticos para MOMENTS_V1.** ¿Podemos mantener sin ambigüedad la diferencia entre contador cero, contador parcial y diagnóstico desconocido al conectar el productor Python con el consumidor C++ ya existente, sin cambiar el contrato numérico?

## 2. Hipótesis falsable y novedad incremental

H1 de ingeniería: en 12 estados sintéticos, el payload V1 y las tres categorías tracked/partial/unknown sobreviven round-trip exactamente (umbral 12/12); mutaciones deliberadas del payload y de metadatos se rechazan. No es hipótesis de mejora matemática, identificación o velocidad. El aporte incremental es una envoltura lateral auditable; clase: adaptación de ingeniería y auditoría semántica, no investigación científica original.

## 3. Estado del arte y prior art

Se revisaron RFC 8785/JCS, RFC 8259, NIST FIPS 180-4, Python 3.12 `json` y `hashlib`, además de Welford/Chan/Higham del programa. La matriz documenta problema, supuestos, evidencia y diferencia en `prior_art_envelope.md`; entradas en `referencias.bib`. La comparación con literatura primaria es acotada a serialización/hash y no permite novedad mundial ni reclamar estándar interoperable.

## 4. Brecha

El wire MOMENTS_V1 transporta estadísticas suficientes para varianza, no diagnósticos históricos. Si importación crea contadores reiniciados a cero, un consumidor podría confundir “no disponible” con “cero medido”. Una futura versión de wire era más riesgosa y no necesaria para probar el contrato lateral.

## 5. Diseño, teoría y configuración

El estimador permanece `s_d²=2^(2e) Q/(n-d)`, para `d∈{0,1}` y `n>d`; no se adapta fórmula ni unidades. El sobre incluye cadena V1 exacta, SHA-256 del payload, origen/partición declarados, estado de disponibilidad, y SHA-256 local del documento. `unknown` fuerza los tres contadores a `null`; `partial` exige subconjunto propio no vacío; `tracked` exige los tres enteros no negativos. Para datos/runtimes/seeds/hardware consultar `config_envelope.json`; el benchmark usa 12 casos generados por semilla fija 831103 y 5 repeticiones por método. No se usó dataset externo.

El digest de documento emplea `json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=False)`. **No** implementa RFC8785/JCS. Hash no es MAC ni firma: un editor puede recomputar. `partition_id` es etiqueta, no prueba disjunción. Se elige serialización Python simple para el MVP; no se traduce mecánicamente el algoritmo a C++.

## 6. Implementación

`src/audit_envelope.py` agrega creación, validación, JSON estable local y verificación. `src/transport.py`, `src/cpp/moments.hpp` y MOMENTS_V1 quedan intactos. `tests/test_audit_envelope.py` incluye roundtrip exacto, unknown vs tracked-zero, partial, corrupción payload/metadatos, claims semánticos incorrectos y payload malformado.

## 7. Tests y benchmark real

El ciclo `bash run.sh` conserva suites previas, compila C++ Release+CTest y ASan/UBSan (LeakSanitizer desactivado con `ASAN_OPTIONS=detect_leaks=0`, por incompatibilidad conocida del entorno), ejecuta cobertura, Ruff, mypy, benchmarks y notebooks. Este incremento añade 11 pruebas (34 Python en total). Los resultados/logs reales se guardan bajo `results/`. El benchmark contrasta JSON envelope con sidecar plano: ambos usan el mismo validador de metadatos, parsean el mismo MOMENTS_V1, verifican payload/registro SHA-256 y comprueban exactamente claims, sin suponer que uno sea más rápido.

## 8. Resultados/tabla/figura

`results/envelope_summary.json` deriva sus indicadores contando aserciones por escenario y réplica: 12 escenarios y 60 round-trips por método, cada uno con payload y claims exactos. Los tamaños/tiempos son mediciones locales descriptivas bajo validaciones equivalentes.

|Formato|Mediana bytes UTF-8|Mediana round-trip ns|P95 round-trip ns|Payload exacto|Claims exactos|
|---|---:|---:|---:|---:|---:|
|Envelope|490|42,510|77,498|60/60|60/60; 12/12 escenarios|
|Sidecar plano|466|27,086|58,388|60/60|60/60; 12/12 escenarios|

El sidecar quedó más compacto y rápido en esta corrida; el tiempo sólo caracteriza estas dos implementaciones Python en el host documentado. `results/envelope_audit.png` muestra ambos. No se extrapola a otros runtimes ni escala productiva.

## 9. Análisis crítico y ablation negativa

El baseline sidecar almacena los mismos claims con hashes y ejecuta las mismas validaciones semánticas; sus pruebas fuerzan también el rechazo de estados incoherentes aunque se recalcule el digest. No se afirma superioridad. Ablation V1-solo pierde status semántico de diagnósticos; el sobre suma bytes y cómputo de hash. Si se omite digest de envelope, los cambios de metadata no se detectan; si se reemplaza unknown-null por cero, la semántica cambia y tests fallan. RFC8785 sería necesario para contrato determinista cross-language; se dejó fuera explícitamente. No se midió con un productor/consumidor de otro lenguaje.

## 10. Limitaciones, sesgos y madurez

El benchmark es sintético y pequeño; la latencia `perf_counter_ns` incluye serializar/verificar/parsing en proceso y no IPC. Las pruebas detectan cambios sin recomputar hashes, no atacantes que puedan recomputarlos. No hay autenticación, autorización, secreto, persistencia, fuente real, prueba de particiones disjuntas o robustez ante volumen adversarial. MADUREZ: incremento local ejecutado/reproducible; la revisión independiente está pendiente y no se declara M2 del dominio ni S2 del programa.

## 11. Comando exacto

`bash run.sh` desde esta carpeta; `MATH_ENV=/ruta/venv bash run.sh` para entorno existente.

## 12. Referencias BibTeX

Ver `referencias.bib`, claves `rfc8785`, `rfc8259`, `nistfips1804`, `pythonjson312`, `pythonhashlib312`, además de Welford/Chan/Higham. Acceso directo listado en `prior_art_envelope.md`.

## 13. Rúbrica original (1–5)

|Dimensión original|Puntuación|Justificación resumida|
|---|---:|---|
|Novedad|1|Adaptación de ingeniería/semántica; no nueva contribución científica|
|Rigor|3|Invariantes explícitos y pruebas, alcance acotado a JSON local y fixtures|
|Reproducibilidad|4|Comando integral, pins y outputs guardados; falta re-review independiente final|
|Código|3|Módulo tipado y testeado, con una API Python local|
|Claridad|3|Derivación/documentación y notebook ejecutado, sin contrato multi-runtime|
|Impacto|2|Utilidad limitada hasta integrar productor instrumentado|
|Honestidad|5|Declara límites de hash, procedencia y comparación de rendimiento|
|MVP|4|Código, tests, CSV/JSON/figura, notebook, refs, config y comando completo|

Puntuaciones internas de este prototipo, no certificación externa.

## 14. Siguiente iteración

Añadir un contrato JCS interoperable sólo si hay consumidor multi-lenguaje; definir claves/amenazas para autenticidad antes de firmar; probar integración con diagnósticos reales instrumentados y preservar `unknown` cuando no existan.

## Avance acumulado del programa

Pregunta central: cómo calcular y conectar resúmenes de momentos estables sin ocultar errores de representación. Incrementos acumulados: 29 cancelación, 30 escala externa, 31 autoescala, 1-nov merge, 2-nov wire+consumer C++, 3-nov status/audit envelope. Tres candidatas revisadas en la tabla de prior art; B (V2) y C (firmas) aplazadas. Ecuación Welford/Chan y varianza no cambian. Resultado positivo: contrato distingue diagnósticos no disponibles de ceros y tests falsifican corrupción. Negativo: overhead local y ninguna autenticidad. Herramienta reutilizable: módulo Python que envuelve MOMENTS_V1 sin tocar el consumidor. Brecha: interoperabilidad JCS y procedencia confiable.

Qué sabemos: el wire numérico no trae historial. Qué construimos: un wrapper lateral que conserva la distinción known/unknown y detecta cambios accidentales. Qué podemos hacer ahora: revisar la integridad del estado exportado sin malinterpretar un contador reiniciado; no podemos afirmar quién generó la muestra ni que particiones sean disjuntas.

## Rúbrica expandida (1–5)

|Dimensión expandida|Puntuación|Justificación resumida|
|---|---:|---|
|Profundidad teórica|2|La ecuación heredada se explica; no se deriva un método nuevo|
|Aporte defendible|2|Adaptación de ingeniería con semántica explícita; no aporte científico original|
|Calidad experimental|3|Baseline con checks equivalentes y resultados contados; escenarios sintéticos pequeños|
|Utilidad|3|Evita convertir desconocido en cero y preserva el wire; falta productor real|
|Reproducibilidad|3|Run integral y CI remota exitosa; re-review independiente del head actual pendiente|
|Honestidad|5|Conserva resultado negativo de tamaño/latencia y alcance no autenticado|
