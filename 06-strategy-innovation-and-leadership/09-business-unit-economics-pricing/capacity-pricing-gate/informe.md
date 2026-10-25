# Ciclo25oct2026 — pricing con capacidad y downside

## 1. Título
Capacity Pricing Gate: precio único exante con presupuestoCVaR y capacidad.

## 2. Hipótesis y novedad incremental
H: el selector devuelve una decisión conCVaR90% de shortfall≤500 bajo los escenarios conocidos. Criterio exacto500+1e−10. Comparar beneficio/riesgo con plug-in de demanda media y política neutral sobre mismos escenarios. La contribución es un componente local ejecutable con masa fraccionaria de cola, capacidad, stop y benchmark; no se reclama invención de revenue management niCVaR.

## 3. Estado del arte y cobertura
Gallego/vanRyzin1994 estudian pricing dinámico e inventarios estocásticos; nuestro motor estático no reproduce su control dinámico. Talluri/vanRyzin2004 libro integra pricing/capacidad y su artículo2004 trata elección discreta general; aquí se fija logística de un producto, no elección de surtido. Rockafellar/Uryasev2000 aporta formulación de optimizaciónCVaR y2002 trata distribuciones generales, importante por átomos.

Cinco referencias conDOI yURL enreferencias.bib. Se verificaron metadata/títulos/autores y resúmenes el25oct en fuentes primarias: ColumbiaBusinessSchool para artículos deGallego/Talluri, Springer para libro y página de publicaciones del autorUryasev para2000/2002. INFORMS devolvió parte de navegación sin contenido, por eso usamos páginas institucionales de autores. No revisión exhaustiva ni lectura completa de libros; no se presenta comparación empírica con sus algoritmos.

## 4. Brecha y selección entre3ideas
Inspección main98659cc (último mergePR78 legal-tech); consulta inicial de PR abiertos vacía. Dominio06 contiene motores09unit economics,04/06/15capital y20EVSI23/24. Tres opciones: extenderEVSI repetía eje23/24; capital con dependencias se solapaba con motores existentes; pricing con capacidad/pérdida adversa complementa el09que solo calcula contribución/LTV. Elegimos tercero y nueva subcarpeta09/capacity-pricing-gate, sin modificar núcleo previo ni globales.

## 5. Diseño, supuestos y configuración
Un precio p para todo escenario antes de conocer demanda. D_s(p)=m_s sigmoid(5−0,25p), m={1000,250,60}, probabilidades{0,6;0,25;0,15}. Son tres escenarios sintéticos de demanda **fluida esperada**, no conteos realizados de clientes. Se sirven min(300,D). Utilidadπ_s=(p−4)servido−1000, donde fijo1000 es evitable al detener. Stop tiene0siempre. Menú contractual{8,10,…,40}; objetivoEπ máximo sujetoCVaR90%(L)≤500, L=max(−π,0).

CVaR implementa promedio del peor10% de probabilidad, partiendo el átomo frontera. No confundir conE[L|L≥VaR], que puede incluir demasiada masa. No esCVaR de pérdida firmada ni regret. Distribución y elasticidad dadas por supuesto, capacidad no optimizada ni costos de ampliarla. Config incluye unidades yseed20261025. No se identifica efecto causal de cambiar precio.

## 6. Implementación
src/pricing.py: Scenario validado, sigmoid estable para extremos, profit, cvar por sorting de átomos, evaluate y choose. Todos precios se evalúan en mismos escenarios y mismo costo. TypedDictDecision; núcleo stdlib sin NumPy/SciPy. ComplejidadO(P SlogS) paraPprecios ySescenarios; memoriaO(P S) por materializar resultados. Stop es opción explícita, no precio artificial. Uso de SciPy solo oracle independienteLP en tests.

## 7. Pruebas y mediciones
6tests pasan; invariantes cubren cola fraccionaria en átomos, α0esperanza, traslación/homogeneidad/monotonía, capacidadcero yprecioextremo sinoverflow, presupuesto anidado, stop yentradas inválidas. OracleLP: min_eta eta+Σw z/(1−α), z≥L−eta,z≥0, comparado a9decimales en4α. Cobertura statements100% de49núcleo, no de todo proyecto. Ruffisolated ymypystrict pasan. Sanitizers/C++ no aplican.

Benchmark selector menú17~0,00069s en corrida inicial, picoPython4832bytes; cifras últimas exactas summary.json. Escalabilidad5repeticiones: mediana17~0,000105s;161~0,000961s;1601~0,010129s. HardwarecompartidoLinuxx86_64/Python3.12.14/NumPy2.3.5, latencias orientativas noSLA. No benchmark de memoriaRSS. No cobertura afirmada de código de plotting/notebook.

## 8. Resultados ejecutados
| Política | Precio |Eπ|CVaR90%shortfall|
|---|---:|---:|---:|
|Plug-in demanda media (revaluado escenarios)|20|2452,000|520,000|
|Neutral escenarios|22|2725,895|592,256|
|Presupuesto500|18|2143,082|477,134|
|Stop|—|0|0|

Plug-in predice3800, pero revaluar esa misma política con escenarios da2452; no implica que tenga desempeño inferior en toda distribución. Restricción reduce beneficio esperado582,813 respecto neutral (21,38%) yCVaR115,122. Bajo precio18, beneficios escenarios3200;1178,608;−477,134. Se cumpleH bajo supuestos.

MC200000elige escenarios según probabilidades configuradas, aplica política fija y evalúa media2141,392(SE3,110) vs exact2143,082: diferencia0,54SE. Esto solo verifica generación/esperanza bajo el modelo, no incertidumbre comercial real. CSVpreserva18opciones incluyendo stop,3beneficios por precio,12escenarios capacidad/presupuesto,3conteos MC,3tamaños de menú;JSON yfigura incluidos.

## 9. Fallos y ablations negativas
No mejora de rentabilidad: se paga valor esperado por cumplir presupuesto. Con capacidad300ybudget0/300 se detiene. Conbudget1000recupera precio22neutral. Menú fino cambia decisión:161precios elige19,2 yEπ2333,560;1601elige19,26 yEπ2342,664 conCVaR499,974. **18es óptimo del menú{8,10,…,40}, no óptimo continuo**. Diferencia199,58 frente grid fino es material; el comité debe autorizar granularidad antes de usar recomendación. Capacidad600 cambia utilidad pero no contiene costo de expansión; no justifica inversión.

## 10. Limitaciones y gobierno
Solo3escenarios, probabilidades elegidas, elasticidad conocida sin datos, omite incertidumbre individualBinomial y min(capacidad,E[D]) no equivaleE[min(capacidad,D)]. El motor implementa explícitamente modelo fluido, no asegura presupuesto sobre ventas aleatorias. No competencia, causalidad, retención, fraude, capacidadendógena, segmentación sensible ni optimización dinámica. Datos sintéticos sinPII. Precio único sin uso de características protegidas. Antes de piloto: calibrar demanda/elasticidad con experimento aprobado, validar costos ybudget con comité, monitorear daño ydrift. ComponenteS2, no validación operacionalM3.

Notebook realmente ejecutado enIPython secuencial namespace fresco ycaptura rich; noQA kernelJupyter (restricción sockets de entorno en ciclosprevios). PNGinspeccionado visualmente, ejes/unidades legibles. QA interfaznotebook completa no realizado. Entorno utiliza paquetes científicos preexistentes envenv system-site-packages yfixa mypy/ruff; contenedor limpio no probado.

## 11. Comando
Desde09-business-unit-economics-pricing/capacity-pricing-gate: `bash run.sh` instala yreproduce. Autor ejecutó `REUSE_ENV=1 PYTHON="$PWD/.venv/bin/python" bash run.sh`. El comando produce tests/cobertura/checks/benchmark/notebook. NoAPI ni credenciales. Dependencias directas fijadas enrequirements.txt, transitivas sinhash.

## 12. ReferenciasBibTeX
Cincoentradas enreferencias.bib conDOI/URLprimario. Revisión acotada segúnsección3.

## 13. Rúbrica autoevaluada
|Criterio|1–5|Justificación|
|---|---:|---|
|Novedad|2|Integración local métodos conocidos|
|Rigor|4|OracleLP, átomos exactos; demanda simplificada|
|Reproducibilidad|4|Config/seed/outputs; freshcontainer pendiente|
|Código|4|Modular tipado ychecks|
|Claridad|4|Stop/unidades/fluido explícitos|
|Impacto|3|Decisión ejecutiva sintética|
|Honestidad|5|Costo beneficio ygridbias declarados|
|MVP|4|Pipelineejecutado; kernelQA pendiente|

## 14. Siguienteiteración
Siguiente iteración recomendada: contrastar modelo fluido con ventas aleatorias ygranularidad autorizada.
1.09-business-unit-economics-pricing/capacity-pricing-gate: integrarBinomial truncada yrecalcularCVaRcon capacidad.
2.09-business-unit-economics-pricing: diseñar experimento de elasticidad con guardrails de ingresos/daño.
3.06-enterprise-capital-allocation-roic: incorporar costo incremental de ampliar capacidad antes de recomendar inversión.

Checklistsrc✓ comando✓ test✓ baseline✓ salidacruda/figura✓ notebookejecutado✓ referencias5✓ informe14p✓ README/MVP/entorno✓ carpeta09✓ madurezlocal✓. Estadosde revisión/publicación separados; no merge automático.
