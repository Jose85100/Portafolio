# Snapshot de adjudicación: semántica, procedencia y disponibilidad —2nov2026

## 1. Título y avance acumulado

Contrato prospectivo local para el programa holdout por identidades.29clausura,30balance,31auditoría completa,1101cotas parciales,1102metadatos de elegibilidad. Mismo programa, no demo aislada. Propiedad exclusiva de este subprograma05; no cambios globales/shared.

## 2. Hipótesis y novedad incremental

H técnica de conformidad:144/144 acuerdo con oráculo independiente sobre semántica/esquema/fuente/fecha efectiva/disponibilidad,0 falsos admitidos/rechazados,72 pares de offsets invariantes; elegibles conservan exactamente fórmula1nov. Config definido antes de interpretar resultados. Aporte local: precondiciones antes documentadas ahora gate ejecutable con motivos y manifiesto. Clasificación auditoría/adaptación de ingeniería, no algoritmo ML nuevo ni contribución científica original acreditada.

## 3. Estado del arte

Cinco fuentes primarias realmente abiertas2nov2026: W3C PROV-DM2013, Python datetime, Feast point-in-time joins, Kapoor/Narayanan2023 textoPMC, Binette/Steorts arXiv2008.04443 resumen/metadatos. prior_art1102.md compara problema/supuestos/método/evidencia/diferencia. No auditoría completa de PROV, integración Feast, lectura íntegra de todos los papers ni búsqueda exhaustiva. No atribuir garantía de disponibilidad a Feast; se compara principio as-of conocido. BibTeX snapshot1102*.

## 4. Brecha, tres ideas y continuidad de pilar

Tabla seiscriterios prior_art1102.md: contrato fuente/semántica/fechas (seleccionado, precondición bloqueante1nov), adjudicación dirigida por coste (requiere costes/verdad humana), DP eficiente (herramienta útil, menor prioridad epistémica). Se justifica continuar pilar02 ML engineering para evitar API fácil de usar mal; rotar solo por calendario dejaría esa brecha. Otros pilares siguen pendientes explícitos, sin afirmar avances en fundacionales/agentes.

## 5. Diseño, configuración y derivación

Snapshot declara K⊆V adjudicado, source_id, schema_version1, semantics complete-equivalence-on-subset, effective_at y available_at awareISO; corte congelado c. Regla G=1 si esquema/fuente/semántica válidos y ambas fechas≤c; normalizar UTC antes de comparar. e≤c no implica a≤c: evidencia retrospectivamente correcta puede llegar después. q exige equivalencia completa entre adjudicados incluidas clases distintas; enlaces positivos incompletos no acreditan eso. Fórmula1nov [L,H] conservada y derivada en notebook/derivacion1102.md con referencia a derivación1101 y sus5508configuraciones. Sin G se bloquea sin inventar cotas. No teorema de desempeño ML; elegibilidad declarada limitada.

config_snapshot1102.json fija144casos=2semánticas×2esquemas×2fuentes×3fechas efectivas×3disponibilidades×2offsets. Datos8filas sintéticas/split4-4, no semillas necesarias porque diseño exhaustivo determinista, no población.864 CSV para6políticas. Hardware/versión reales environment.json/versions.txt; dependencias fijadas requirements.txt, sin fuentes externas de datos. Corte12UTC es escenario sintético configurado, no afirmación de disponibilidad real en esa hora.

## 6. Implementación

src/snapshot_gate.py dataclasses tipadas AdjudicationSnapshot/GateResult, prospective_audit y verify_manifest. Reutiliza components29/partial_audit1nov. Excepciones explícitas para fechas inválidas/sin zona, IDs/asignación inválidos. Incompatibilidad semántica/temporal produce blocked con motivos; metadata-eligible no significa fuente auténtica ni validación empírica. Manifest incluye payload canónico de observados/adjudicados/asignación/corte; SHA256 detecta cambio sin actualizar digest, no firma ni autenticación. Copia asignación para evitar mutación externa de manifest. Complejidad O(n log n+L_id+B), memoria O(n+L_id+B) incluyendo bytes serializados; no coste gratis. Python mantiene coherencia de API/notebook; no traducción multilenguaje injustificada, EL83 y motores C++ intactos.

## 7. Ejecución, tests y benchmarks

46 tests pasan:36 regresión+10 nuevos (UTC,naive/error,frontera1µs,effectivefuture,availabilityfuture,semántica/fuente/esquema,orden/hash/tamper/copia,IDs,negativo fuente). Heredadas5508configuraciones de extremos parciales siguen pasando. Ruff src/tests/benchmarks y mypy5núcleos estricto pasan; no cobertura de líneas medida.144casos144/144oráculo,72/72paresoffset mismo manifiesto. Notebook6celdas ejecutadas realmente con outputs/2figuras; IPython secuencial en proceso, no kernel aislado ni frontend Jupyter completo.12 mediciones de escala (3repeticiones×4tamaños28–28000),incluyen hash+auditor, excluyen instalación/I/O/carga/render. No C++ nuevo: no sanitizers pertinentes. Resultados sintéticos de conformidad, no modelos entrenados ni validación empírica.

## 8. Resultados exactos y gráficos

|Política|Admisiones/144|Admisiones inadmisibles|Elegibles rechazados|
|---|---:|---:|---:|
|Maluso explícito1101 sin metadatos|144|136|0|
|Solo semántica/esquema/fuente|18|10|0|
|Además solo fecha efectiva|12|4|0|
|Referencia as-of independiente|8|0|0|
|Gate prospectivo|8|0|0|
|Abstención total|0|0|8|

No se debilita baseline competitivo: gate **empata** disciplina as-of conocida. Maluso1101 es ablation de precondiciones, no competidor científico. Oráculo usa enteros del diseño, no parser del gate. policy.png compara errores de política, no fuga predictiva; cost.png escala temporal/memoria. PNG inspeccionados realmente por autor, ejes/unidades/valores legibles, sin recortes. Crudos raw.csv/scale.json, manifests.json144 entradas, negative.json. Tiempos dependen del host,tracing y tamaño payload; no prometer velocidad superior ni coste monetario no medido.

## 9. Crítica y negativos

Bloquear por disponibilidad evita4admisiones que event-time-only aceptaba en este diseño; no prueba frecuencia en negocio. Abstenerse siempre evita inadmisibles pero pierde8elegibles. Fuente/semántica/fechas falsas formalmente válidas pueden pasar: negativo reporta cota0 frente8filas realmente expuestas. Recalcular hash tras falsificar fuente pasa verificación; checksum nunca autentica. Conservar negativos evita confundir metadata gate con seguridad o validación de verdad.

## 10. Limitaciones y sesgos

Se confía en declaraciones del proveedor, no firma/log externo ni auditoría humana. Identidades se asumen estáticas/aplicables al caso histórico; no validez final/expiración/cambios de identidad. No asegura temporalidad de enlaces observados usados por splitter antes del gate, features,labels,tuning o selección. Dataset diseñado pequeño, no tasa empírica ni intervalos inferenciales, AUC,causalidad o regulación. Metadatos ausentes impiden uso prospectivo; solo diagnóstico retrospectivo requiere política separada, no backdating automático. No garantía de madurez M2/M3 del dominio.

## 11. Comando exacto reproducible

Desde05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout:

```bash
bash run_snapshot_gate.sh
```

Instala .venv con requirements.txt,46tests/lint/tipos/benchmark/notebook. Reuso verificado `PYTHON="$PWD/.venv/bin/python" SKIP_INSTALL=1 bash run_snapshot_gate.sh`. Python3.12+/pip inicial, Linux para registroCPU, sin credenciales/datasets privados. Instrucciones reproducibles sustituyen Dockerfile. Valores deterministas sí, ns/bytes no idénticos entre reruns. Resultados anteriores se preservan.

## 12. Referencias BibTeX

referencias.bib añade snapshot1102prov,datetime,feast,leakage,entity; URLs/fecha/alcance en prior_art1102.md y results/snapshot1102/references_verified.json. No referencias simuladas ni certificación de revisión íntegra donde solo se abrió resumen.

## 13. Rúbricas y madurez

Autoevaluación provisional1–5: novedad2 (contrato/as-of conocido), rigor4 (reglas/oráculo/regresiones), reproducibilidad4 (sin kernel aislado), código4,claridad4,impacto3 (sin datos reales),honestidad5,MVP4. Adicional: profundidad teórica3,aporte defendible3,calidad experimental3,utilidad4,reproducibilidad4,honestidad5. No sustituyen dictamen independiente. Experimental ejecutado; revisión/publicación/CI separadas en consolidado, no operacional ni validado en negocio, no equivalencia automática S2/M2.

## 14. Siguiente iteración y decisión

Continuar con fuente adjudicada aprobada y disponibilidad verificable externamente; ajustar si solo hay enlaces positivos o llega tarde; cerrar claims de autenticación/ausencia total de fuga por hash/gate. Ahora podemos bloquear llamadas declaradamente inadmisibles y preservar qué snapshot/corte/asignación se evaluaron; antes solo advertíamos sus supuestos. Pendiente garantizar procedencia real y observado temporal sin crear demo aislada. research-log/roadmap conservan decisiones/negativos.

Checklist: README✓src✓tests✓config✓requirements✓comando✓CSV/JSON✓2figuras✓notebookejecutado✓fórmulas✓5refs✓priorart✓3ideas✓baselinejusto/oráculo✓negativos✓14p✓ambasrúbricas✓researchlog/roadmap✓. Cobertura, autenticidad, kernel aislado y validación empírica no certificados. Estado revisión/PR/CI en consolidado, no equiparar archivo con ejecución o publicación.
