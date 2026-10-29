# Ciclo de I+D+i — 28 de octubre de2026

## 1. Título
Incentive Alignment Gate: auditar la respuesta del ejecutivo antes de aprobar un bono.

## 2. Hipótesis y novedad incremental
H: existe un contrato del menú que implementa prudent con margenIC≥0,05, participación≥0 y beneficio incremental firma≥0. Resultado: fracción diferida contingente0,9, margen0,30, participación8,55 y beneficio neto8,95. La contribución local es auditar elección endógena del agente y fallos del conjunto modelado; no inventa teoría de agencia ni una regulación de remuneración.

## 3. Estado del arte
Holmström1979 estudia acción privada y observabilidad; Holmström/Milgrom1991 advierte sobre incentivos entre tareas; Jensen/Meckling1976 enmarca costos de agencia. Baker1992 conecta medidas de desempeño y objetivos del principal, y Baker/Gibbons/Murphy1994 estudia medidas objetivas/subjetivas. Nuestro modelo es más pequeño: acciones finitas y bono contingente, no reproduce contratos óptimos de esos trabajos.

Cinco referencias reales DOI/URL enreferencias.bib. Verificación28oct mediante búsquedas de editores, página institucional MIT de Holmström y metadata indexada original. MIT abrió yconfirmó1979/1991; OUP redirección falló, ScienceDirect yChicago devolvieron403. Se verificaron título/autores/identificadores yresúmenes indexados, no se leyó íntegra toda literatura. No revisión exhaustiva ni prioridad mundial.

## 4. Brecha y3ideas
Main5b7d30e; consulta de PRabiertos vacía al inicio. Se compararon: extender fondeo repetiría27; scorecard descriptivo ya existe07; auditar IC de diferimiento en13cubre brecha. Motor13 previo aplica malus ydivide pagos, sin preguntar qué acción prefiere un ejecutivo. Aquí se calcula esa elección, no se impone prudent al evaluar el contrato. No se alteran globales ni motores anteriores.

## 5. Modelo y configuración
Dos acciones sintéticas: prudent(volumen100,qfracaso0,05,beneficioéxito20/fracaso−10,esfuerzo1); volume_chasing(150,0,5,35/−50,0). Bono base B=0,1×volumen, fracciónf∈{0;0,25;0,5;0,75;0,9;1}. Pago éxitoB, fracaso(1−f)B. Fracción diferida se pierde al fracasar: no es solo una fecha de pago distinta. Responsabilidad limitada: pagos entre0yB, nunca cobranza negativa al agente.

Ebono=B(1−fq); utilidadagente=Ebono−esfuerzo; beneficiooperativoesperado=(1−q)πéxito+qπfracaso; beneficiofirma=Eπ−Ebono. Todos valores sintéticos, esfuerzo en equivalente monetario de utilidad, agente neutral al riesgo, sin descuento ni salario fijo. Resultado es observable yno manipulable por supuesto. Alternativa externa da utilidad0yvalor0a firma para ese proyecto.

Diseñador elige menor f del menú con utilidadobjetivo−máxima utilidadalternativa≥0,05, utilidadobjetivo≥outside, acción efectivamente elegida=objetivo ybeneficiofirma≥0. No maximiza beneficio del principal sobre todos contratos, tasas o acciones. Desempates de mejor respuesta son adversos a firma: no se presume implementación favorable en indiferencia.

## 6. Implementación
src/incentives.py: Action validada, evaluate, response, audit ydesign con TypedDict. NombreOUTSIDE reservado, probabilidades0..1yentradas finitas, menú0..1. Núcleo stdlib. Auditoría separaICentre acciones deIRfrente al exterior. El filtro de acción implementada evita aceptar un empate con abstención. ComplejidadO(KA) paraKcontratos yAacciones; memoriaO(KA) por resultados materializados. No se convierte esta enumeración en un teorema de comportamiento real.

## 7. Tests y benchmarks
5tests pasan: frontera analítica de dos acciones, identidad transferencia netprofit+bono=grossprofit, esperanza de pagos por estados, límites0..B, respuesta baseline/diseño, outside alto, desempate adverso, tope inviable, acción omitida yentradas inválidas/acciónúnica. Cobertura100% de61statements núcleo, no todo proyecto/notebook. Ruffisolated ymypystrict pasan. NoC++ ni sanitizers aplicables.

Oracle analítico independiente: IC=−6+7f; margen0,05requieref≥6,05/7=0,864285714. Evaluación numérica reproduce ese margen; menú elige0,9. Benchmark menú6y2acciones ~0,000314s y3772bytes picoPython(tracemalloc) en corrida autor; valores exactos últimos enJSON. Escala2/20/200acciones con alternativas duplicadas yrenombradas,5repeticiones: medianas0,000040/0,000218/0,002118s; f0,9estable. Duplicar alternativas mide cómputo, no diversidad ni evidencia nueva. NoRSS niSLA. Python3.12.14/Linuxx86_64 en metadatos; cálculo determinista sin seeds/MC inventados.

## 8. Resultados ejecutados
| Contrato / benchmark | Respuesta | Utilidad agente | Beneficio neto firma |
|---|---|---:|---:|
|Bono inmediato f0|volume_chasing|15|−22,5|
|Abstenerse del proyecto|OUTSIDE|0|0|
|f0,9del menú|prudent|8,55|8,95|

Con f0,9, acciónalternativa obtiene8,25: margen0,30. Bono esperado prudent9,55, beneficio operativo18,5, neto8,95. Prima de participación8,55. El benchmark fuerte0evita vender una mejora31,45sobre un contrato heredado malo como beneficio contra una alternativa racional: incremento frente abstención8,95. No evidenciaempírica de mejora31,45ni8,95.

CSV conserva6contratos conrespuesta yvalores;3nivelesqalternativa0,1/0,3/0,5;3tamaños de acción. JSON incluye baseline/diseño/stress/frontera; notebook muestra tablas yfigura. Las líneas del gráfico conectan puntos del menú para lectura, no implican optimización continua.

## 9. Negativos y ablations
Topef0,8no permite implementar objetivo. Si qalternativa0,1o0,3no existe contrato del menú que alinee con margen, incluso difiriendo100%; no inventamos una solución. Una acción omitida(volumen300,q0,01,beneficios0/−100,esfuerzo0) recibe utilidad29,73con f0,9, desplaza prudent ydeja netprofit−30,73: la auditoría falla si el conjunto de acciones es incorrecto. Más complejidad del contrato no garantiza alineación global.

El mecanismo reduce remuneración esperada por pérdidas, no elimina pérdidas operativas ni garantiza conducta humana. La firma podría modificar rate, métricas, funciones yparticipación; nuestro mínimo de diferimiento no es contratoóptimo universal. No se cuenta bonus como creación de valor: se resta de beneficio operativo.

## 10. Límites y gobierno
Solo2acciones conocidas inicialmente; probabilidades ybeneficios elegidos, no estimados. Riesgoneutralidad, costo de esfuerzo conocido, resultado cierto/observable ysin manipulación, sin descuento, salario, reputación, repetición, renegociación, selección o normas laborales. Deferral contingente es una especificación matemática, no afirmación de legalidad de malus/clawback. Se requiere revisión contractual yvalidaciónempírica antes de aplicación real; no se prescribe remuneración a personaalguna.

ComponenteS2 sintético, programa13sinrecertificar. Notebookejecutado realmente enIPython en proceso, namespace fresco ycapturarich; noQA de kernelJupyter. PNGinspeccionado, ejes/leyendas/valores legibles; interfaznotebook completa noinspeccionada. Entornocon paquetes científicos disponibles; segundo contenedorlimpio no probado.

## 11. Comando exacto
Desde13-executive-incentive-design/incentive-alignment-gate: `bash run.sh` instala yreproduce. Autor: `REUSE_ENV=1 PYTHON="$PWD/.venv/bin/python" bash run.sh`. Dependencias directas fijadas, transitivas sinhash. RequierePython3.12 yacceso alíndice para instalación; sinAPI ni datosprivados.

## 12. Referencias BibTeX
Cincoentradas enreferencias.bib, DOI/URLverificados; cobertura ybloqueos de acceso explícitos en sección3. No se atribuye a la literatura nuestro caso sintético.

## 13. Rúbrica autoevaluada
|Criterio|Nota1–5|Motivo|
|---|---:|---|
|Novedad|2|Integraciónlocal de teoría clásica|
|Rigor|4|Oracle yIC/IR explícitos; acciones simplificadas|
|Reproducibilidad|4|Config/checks/outputs; freshcontainer pendiente|
|Código|4|Núcleotipado/validado|
|Claridad|4|Contingencia, transferencias ybaseline fuerte|
|Impacto|3|Auditoría ejecutiva sintética|
|Honestidad|5|Falla poracciónomitida yobjetivo limitado|
|MVP|4|Pipelineejecutado; kernelQA pendiente|

## 14. Siguiente iteración
Siguiente iteración recomendada: validar acciones ymedidas de calidad antes de ampliar contratos.
1.13-executive-incentive-design/incentive-alignment-gate: agregar aversión al riesgo ydescuento manteniendoIC/IR.
2.21-executive-governance-board-decisions: definir evidencia de que una métrica es observable yno manipulable.
3.13-executive-incentive-design: comparar abstención, bono fijo yotras tasas en igual conjunto de acciones aprobado.

Checklist src✓ comando✓ tests✓ baseline✓ resultados/figura✓ notebookejecutado✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta13✓ madurezlocal✓. Revisor independiente reprodujo pipelineexit0 yrevisó núcleo sinbloqueantes. Publicaciónseparada, sinmerge automático.
