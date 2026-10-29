# Ciclo de I+D+i — 29 de octubre de2026

## 1. Título
Quorum Common-Cause Gate: disponibilidad conjunta del comité frente a asistencia marginal.

## 2. Hipótesis y novedad incremental
H: independencia de probabilidades marginales puede aprobar erróneamente una meta de disponibilidad0,85; un plan del menú medido con la distribución conjunta sí alcanza la meta. Resultado: baseline0reservas predice0,8512, pero vale0,76;2reservas dan0,9139. La contribución local es una auditoría pequeña de resiliencia y factibilidad, no una teoría nueva ni evidencia de buen gobierno empresarial.

## 3. Estado del arte y fuentes
Adams/Hermalin/Weisbach2010 revisan gobierno yselección endógena de directores; Fama/Jensen1983 separan decisión ycontrol; Schwartz-Ziv/Weisbach2013 estudian actas reales. No inferimos disponibilidad ocalidad a partir de sus resultados. Hong2013 trata distribuciones Poisson-binomial independientes: antecedente del baseline, sin reproducir su algoritmo. Marshall/Olkin1967 motiva causas comunes mediante shockmodels continuos; aquí usamos una mezcla Bernoulli discreta, no su distribución exponencial.

Cinco referencias DOI/URL verificadas29oct en páginas originales indexadas e instituciones. ChicagoUnbound, Stanford yHebrewUniversity abrieron metadata; AEA/ScienceDirect devolvieron403. Se revisaron metadata/resúmenes, no íntegramente todos artículos. Stanford hospeda versión de reporte1966del artículo1967. No revisión exhaustiva ni prioridad científica.

## 4. Brecha y3ideas
Se actualizó worktree a main022f6bd; PR99de riesgo abierto al consultar, sin solape06. Tres ideas: atribución Shapley requeriría valores de coalición no disponibles; más incentivos repetiría28; disponibilidad de comité con ausencias comunes cubre21S1. Búsqueda local no encontró quorum/attendance/commonshock en06. El programa21 diseña derechos ysupervisión; este componente implementa solo disponibilidad operativa, no voto jurídico.

## 5. Modelo y configuración
Miembrosbase4: risk_lead yA/B/C. EventoE: sumX≥3yX0=1. Normalpeso0,8conp=(0,95;1;1;1); disrupciónpeso0,2conp=(0,95;0;0;0). Independencia condicional a régimen, dependencia incondicional enA/B/C. Menú0/1/2reservas, cada una conp0,9enambosregímenes, independencia mutua ydelrégimen por supuesto. Costo unitario1sintético, meta0,85.

P(E)=Σ_r w_rΣ_x I(E(x))Π_i[p_ri si x_i=1,1−p_ri si0]. Baseline usa producto de marginales p_i=Σw_rp_ri ypierde correlación. Selector minimiza costo entre planes que alcanzan meta, sin cambiar mínimo3nirolobligatorio. Todos participantes extra se suponen autorizados y elegibles; son adicionales al comité, no sustituyen risk_lead. Mínimo fijo3representa menor fracción al ampliarN: no es una regla de mayoría proporcional, yno se aplica directamente a estatutos de junta.

## 6. Implementación
src/quorum.py: Regime, validate, enumerate_states, exact, independent_marginals, add_standbys ychoose. Valida pesos positivos normalizados, probabilidades0..1, dimensiones, quorum entero ymandatorios únicos válidos. Enumeration guarda también masas0, útil para auditar totalidad del espacio. Tope16miembros por costo exponencial; O(RN2^N) tiempo yO(R2^N) memoria. El rol obligatorio es presencia, no autoridad de veto ni voto favorable.

## 7. Tests ybenchmarks
5tests pasan: oracle cerrado de causa común yreservas, binomial independiente paraN1..6, conservación de masa, rol obligatorio, extremos deterministas, cota delrol, falso pase, inviabilidad yentradas inválidas. Oraclebase:0,95×0,8=0,76; con2reservas:0,95(0,8+0,2×0,9²)=0,9139; marginal:0,95(3×0,8²×0,2+0,8³)=0,8512.

Cobertura100% de66statements núcleo, no notebook ni todo repositorio. Ruffisolated ymypystrict pasan. Benchmark menú3planes(224máscaras entre2regímenes) ~0,0058s contracemalloc y32841bytes picoPython en corrida inicial; última cifraexactaJSON. Escala4/6/8miembros:32/128/512estados,5repeticiones, medianas0,000044/0,000205/0,000988s. NoRSS, SLA ni escalabilidad empresarial. Python3.12.14/Linuxx86_64. Determinista; no MonteCarlo ni intervalos inventados. SinC++/sanitizers aplicables.

## 8. Resultados
| Reservas | Exacta | Independiente marginal | Costo |
|---:|---:|---:|---:|
|0|0,7600|0,8512|0|
|1|0,7600|0,93328|1|
|2|0,9139|0,947644|2|

Errorbase+0,0912=9,12puntos porcentuales. Exacto recomienda2reservas para meta0,85, mejora15,39puntos reales **dentro del modelo** respecto al plan0.1reserva no mejora el caso de disrupción: risklead+1solo son2<3. Normalmente ya sobran personas; añadir una sola no cubre el shock. Costo2no se transforma en retorno financiero.

CSVplanes y224filas crudas de masas,4pesos de shock y3tamaños de escalabilidad, JSON yPNG preservados. Figura ynotebook muestran meta/error/decisión. No hay datos de compañías ni asistencia observada.

## 9. Falsación ynegativos
Peso shock0,1permite0reservas yP0,855;0,4requiere2yP0,8778;0,8no permite planfactible. Si meta0,97supera presencia0,95delmiembroobligatorio, es imposible sin cambiar ese supuesto. Aumentar mínimoa4tampoco es factible enmenú. No se reduce quorum para fabricar resultado. La independencia no sobreestima siempre: la dirección depende del evento ydependencia, por lo que este caso no prueba una regla universal. Supuesto de reservas fuera de causa común es crucial ydebe contrastarse.

## 10. Límites y gobierno
Disponibilidad no implica aprobación, deliberación, calidad, independencia decriterio, validez jurídica ni ausencia deconflictos. Las reservas deben estar autorizadas por reglas reales antes de que cuenten; este modelo no puede autorizarlas. No recomendación legal ni cambio de estatutos. Probabilidades/regímenes elegidos, no estimados; no calendario, secuencia de reuniones, duración, recusa, revocación o correlación propia entre reservas. El costo es una unidad abstracta, no presupuesto de personal real.

ComponenteS2 sintético, programa21conservaS1fuera deél. Notebookejecutado realmente IPython secuencial, namespace fresco ycaptura rich; noQA de kernelJupyter. PNGinspeccionado; interfaz notebook completa no inspeccionada. Venvusó paquetes científicos disponibles yherramientas fijadas; contenedor limpio adicional pendiente.

## 11. Comando exacto
Desde21-executive-governance-board-decisions/quorum-common-cause-gate: `bash run.sh` instala yreproduce. Autor: `REUSE_ENV=1 PYTHON="$PWD/.venv/bin/python" bash run.sh`. Dependencias directas fijadas, transitivas sinhash. Python3.12yíndice para instalación; sinAPI niPII.

## 12. Referencias BibTeX
Cincoentradas enreferencias.bib. DOI ymetadata verificados, alcance ybloqueos explícitos en sección3. No se presenta nuestra mezcla como réplica delos papers.

## 13. Rúbrica autoevaluada
|Criterio|Nota1–5|Motivo|
|---|---:|---|
|Novedad|2|Integración local, probabilidad clásica|
|Rigor|4|Oracles ymasa exacta; supuestos pequeños|
|Reproducibilidad|4|Config/estados/checks; freshcontainer pendiente|
|Código|4|Tipado/validado, límite de tamaño|
|Claridad|4|Evento de disponibilidad separado de decisión|
|Impacto|3|Prueba ejecutiva sintética|
|Honestidad|5|Dependencia yautorización son supuestos|
|MVP|4|Pipelineejecutado; kernelQA pendiente|

## 14. Siguiente iteración
Siguiente iteración recomendada: validar dependencia y elegibilidad antes de diseñar reservas.
1.21-executive-governance-board-decisions/quorum-common-cause-gate: modelar reservas también afectadas por causa común.
2.21-executive-governance-board-decisions: separar reglas reales de elegibilidad/recusa delmodelo probabilístico.
3.07-executive-strategy-okr-operating-system: registrar cancelaciones ytiempo hasta decisión con datos aprobados, sin inferir calidad porasistencia.

Checklist src✓ comando✓ tests✓ baseline✓ estadoscrudos/figura✓ notebookejecutado✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta21✓ madurezlocal✓. Revisor independiente reprodujo pipeline exit0 y revisó núcleo sin bloqueantes. Revisión ypublicación separadas; sinmerge automático.
