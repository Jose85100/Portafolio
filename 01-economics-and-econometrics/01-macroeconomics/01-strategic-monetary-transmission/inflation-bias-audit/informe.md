# Informe crítico acumulativo30 — 2026-10-30

## 1. Título y decisión

Delegación conservadora: cuánto sesgo reducir sin sacrificar excesivamente estabilización. Extensión del programa Strategic Monetary Transmission y de su MVP29; no nueva carpeta ni sustitución de pruebas previas. Decisión interna del modelo: elegir peso delegado q minimizando pérdida social común. No recomendación para un banco central real.

## 2. Hipótesis y clasificación de aporte

H1: la raíz monotónica q* produce J(q*)≤J(λ)+1e−10 para toda la malla; coincide con oráculo independiente y promedio de estados≤1e−10. H2 negativa: q0 empeora si k0 y σ>0. Contribución **computacional acumulativa/educativa**, especialización explícita de teoría clásica, no innovación teórica o prioridad mundial. La novedad respecto al repositorio es evaluar objetivos delegados con un objetivo social fijo, conservando consistencia RE y código29.

## 3. Estado del arte: matriz verificada

Referencias y metadatos contrastados 2026-10-30 en editor/autor; BibTeX íntegro en referencias.bib. No se afirma reproducir todo artículo.

|Referencia|Mecanismo previo|Aquí se reutiliza|Fuera de alcance|
|---|---|---|---|
|Kydland–Prescott1977, DOI10.1086/260580, Chicago|Inconsistencia temporal|Baseline compromiso/discreción29|Planes dinámicos generales|
|Barro–Gordon1983, DOI10.1086/261167, Chicago|Sesgo bajo tasa natural|BR y expectativas RE|Estimación de política|
|Barro–Gordon1983, DOI10.1016/0304-3932(83)90051-X, ScienceDirect|Reputación repetida|Motiva alternativa no elegida|Equilibrio reputacional|
|Rogoff1985, DOI10.2307/1885679, Oxford|Ganancia inflacionaria/coste estabilización|Tradeoff de peso conservador|Modelo completo del artículo|
|Walsh1995, URL people.ucsc.edu/~walshc/Select.htm|Contratos monetarios|Contraste institucional|Transferencias e incentivos contractuales|

URLs verificadas en referencias.bib; título/autores/año/volumen/páginas/DOI cuando existe. Walsh usa URL del autor, no DOI inventado. Lectura de metadatos y mecanismo general, sin atribuir como nuevo un teorema clásico.

## 4. Brecha y selección entre tres ideas

Aprendizaje adaptativo: útil, pero cambia hipótesis RE y abre dinámica. Reputación repetida: conecta credibilidad, pero exige juego repetido y multiplicidad. **Delegación estática**: seleccionada porque cierra una fricción dejada por29 con menor alcance y permite comparar objetivos sin inconsistencia. Aún supone nombramiento creíble sin coste; no resuelve instituciones. El programa general heterogéneo/Markov sigue S1, componente estático S2, sin equivalencia automática S2/M2.

## 5. Diseño, configuración y derivación

Fuente: estados sintéticos ε∈{−σ,+σ} equiprobables, expectativas exactas. Sin muestreo/seed, no error Monte Carlo. α∈{.5,1,2}, λ∈{0,.5,1,2}, k∈{0,.5,1}, σ∈{0,.5,1,3}:144casos. config previa29 conservada; delegation-config.json registra extensión, plataforma/versión/costes/hash en resultados. Python3.12.14, CPU genérica Linux-6.18.57-x86_64-with-glibc2.39; CPU exacta no identificada, sin acelerador.

Original: y=α(π−πe)+ε, banco y sociedad minimizan Lλ=.5[π²+λ(y−k)²]. Modificación: banco Lq, sociedad sigue Lλ. πe=qαk, π=qαk−qαε/(1+qα²), y=ε/(1+qα²). Entonces J(q)=.5[(qαk)²+λk²+σ²((qα)²+λ)/(1+qα²)²]. Derivación LaTeX paso a paso en notebook, incluyendo factores y unidades normalizadas. Condición de primer orden equivalente F(q)=q k²(1+α²q)³+σ²(q−λ)=0. F' = k²(1+α²q)²(1+4α²q)+σ²>0 salvo k=σ=0. Signos en extremos garantizan raíz única en[0,λ]; J'>0 fuera de λ, por tanto mínimo global q≥0. Casos degenerados: k0→qλ; σ0,k>0→q0; ambos0 se elige baseline entre indiferentes. No se presupone convexidad global de J.

## 6. Implementación

src/delegation.py tipado y modular; brentq raíz xtol1e−14; scipy bounded minimiza directamente J como oráculo con extremos explícitos. `state_average` reutiliza **policies y loss de29**, verificando fórmula agregada contra estados bajo objetivo social. src/run_delegation.py genera CSV, JSON, figura y hashes. No C++ añadido: duplicar este solver escalar no aporta; no CMake/sanitizers aplicables al cambio Python.

## 7. Tests y benchmarks reales

`bash run.sh` local exit0:7tests total (3nuevos,4previos); cobertura medida65/67statements97%, monetario28/29 y delegación37/38. Se cubren144combinaciones/invariantes deterministas; no se etiqueta property-based aleatoria. Ruff limpio, mypy5src limpio con ignore-missing-imports; no tipado de scipy garantizado. Suite común8/8 independiente, log common-suite30.log. Oráculo, límites degenerados, NaN/inf y no empeoramiento incluidos. Rama de fallo del solver no simulada. No RSS ni coste operacional medidos.

## 8. Resultados, tablas y figuras

|Ancla α=λ=k=σ=1|Peso q|Pérdida social esperada|
|---|---:|---:|
|Discreción baseline|1|1.25|
|Delegación óptima|0.308571201|0.867405650|
|Extremo q0|0|1.0|
|Compromiso creíble de29|regla contingente|.75|

Ganancia delegación frente baseline30.60755%; aún peor que compromiso asumido. Máximo error oráculo 3.55e-15, fórmula/estados 4.44e-15, umbral1e−10 pasa. results/delegation.csv crudo, delegation-summary.json, delegation.png. Barrido instrumentado 0.3111s, pico Python 107128bytes: hardware/medición específica, no intervalo estadístico ni benchmark entre lenguajes. Sensibilidad de figuras evalúaσ0..4; dominio de tests usa malla finita. Figura inspeccionada visualmente: etiquetas/leyendas legibles.

## 9. Análisis crítico y ablations negativas

Si k0, q0 genera J=.5 frente baseline .25 para α=λ=σ1: el consejo universal de endurecer es falso. Si σ0,k1, q0 da .5 frente baseline1: sin shocks, el tradeoff desaparece. Evaluar Lq en lugar de Lλ sería baseline injusto y no se hace. Compromiso29 es una cota útil pero requiere capacidad distinta. La reducción de pérdida en parámetros conocidos no demuestra una recomendación robusta a α mal medido.

## 10. Limitaciones y sesgos

Lineal-cuadrático, un periodo, información perfecta del shock al banco, privados RE, preferencias/α conocidos, nombramiento creíble y sin coste. No fricción de selección/captura ni validación empírica, identificación causal, heterogeneidad, tasas financieras o sistema bancario. No credibilidad endógena, reputación o gobernanza real. Todo normalizado, no datos o porcentajes macro. No claim regulatorio. El muestreo de parámetros no prueba robustez fuera del dominio; resultado analítico depende de supuestos declarados.

## 11. Comando exacto y presentación

Desde la raíz del repositorio:

```bash
cd 01-economics-and-econometrics/01-macroeconomics/01-strategic-monetary-transmission/inflation-bias-audit
bash run.sh
```

Instala pins en .venv y ejecuta todo. notebook.ipynb:8celdas de código secuenciales en IPython limpio en proceso, errores abortan, outputs guardados y nbformat validado. Figura vista; no frontend completo de notebook inspeccionado. Para inspección humana abrir notebook.ipynb en JupyterLab. Método explícito sin kernel/socket; no afirmar ejecución nbclient. Config, hashes y logs incluidos; tiempo/pico pueden variar al reproducir.

## 12. Referencias BibTeX

referencias.bib: cinco entradas reales con DOI/URL de sección3. La bibliografía del ciclo29 permanece vigente y fue revalidada para30; no inventar cinco nuevas referencias decorativas. No se descargaron datos de terceros; salidas generadas determinísticamente desdeconfig y fuente versionada.

## 13. Rúbrica 1–5 y checklist

Autoevaluación (no puntuación independiente): novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4. La deducción es exacta dentro de modelo; falta coste institucional y datos, razón de no5en rigor/impacto. Checklist cumplido local: src✓ tests✓ baseline numérico✓ CSV/JSON✓ PNG✓ notebook ejecutado✓ informe14p✓ config✓5refsBibTeX✓pins✓ comando único✓ MVP✓ README✓ registro/roadmap✓. CMake/ctest/sanitizers N/A Python. Revisión independiente solicitada, ver informe consolidado del coordinador para dictamen y enlacePR; publicación no equivale a validación operacional ni S4.

## 14. Siguiente iteración

Continuar si se incluye coste explícito de nombramiento; ajustar si el coste supera ganancia social; cerrar esta variante si ningún q mejora baseline dentro de incertidumbre de parámetros. Tres tareas concretas: src/delegation.py incluir coste institucional; src/run_delegation.py medir arrepentimiento bajo α mal especificado; README del programa formalizar estado e información para futura conexión Markov. Preservar expectativas consistentes, objetivo social común y controles negativos al ampliar.


# Ciclo31 — Ambigüedad de varianza y delegación minimax regret

1. **Título/programa.** Auditoría acumulativa de transmisión monetaria estática:29 expectativas,30 delegación conocida,31 decisión con intervalo de varianza. Pregunta central: qué reglas mejoran pérdida social respetando información y expectativas.
2. **Hipótesis/novedad incremental.** Mejora técnica/utilidad, no causal: minimizar peor regret no empeora plug-in medio a1e−10 y coincide con oráculo independiente a1e−8. Criterios fijados antes de interpretar; experimento diseñado, no datos empíricos. Clasificación adaptación de ingeniería/auditoría, no innovación teórica.
3. **Estado del arte.** Seis fuentes primarias verificadas en prior-art31.md; referencias.bib. Minimax regret y delegación conservadora son conocidos. No afirmar novedad disciplinar por combinarlos.
4. **Brecha/tres ideas.** Credibilidad endógena: alto valor pero exige otro juego; identificación empírica: alto valor pero falta diseño/dataset; ambigüedad de varianza: elegida por reutilización, alcance completo y evidencia exacta factible. No selección por nombre novedoso. Falta intervalo empírico.
5. **Diseño/config.** ambiguity-config.json:144combinaciones α∈{0,5;1;2},λ∈{0,5;1;2},k∈{0;0,5;1;2},intervalos[0,1],[0,04;4],[1,16],[1,1]. Seed no aplica a expectativa exacta. Hardware/versiones/hash reales en JSON. Parámetros normalizados, no tasas calibradas.
6. **Implementación/teoría.** src/ambiguity.py tipado reutiliza social_loss/optimal_weight. Fórmula original J=A+vB; propuesta minq maxv[J−minzJ]. Derivación completa de convexidad en v, monotonía q*(v) y raíz de regrets en derivacion31.md/notebook. Conserva juego, RE y evaluación social; pierde optimalidad puntual cuando v se conoce. Un intervalo que excluye verdad elimina garantía. Sin lenguaje adicional porque duplicar solver escalar no mejora decisión.
7. **Tests/benchmarks.** bash run.sh exit0:12 unitarios (5nuevos/7regresión), casos inválidos/degenerados, propiedades27regímenes×31puntos interiores, oracle; Ruff/mypy7archivos pasan. Cobertura medida src.ambiguity25/25sentencias100%; total90/92=98% redondeado. No cobertura de ramas reclamada. Común8tests aparte. Escalar SciPy bounded + búsqueda ternaria150iteraciones objetiva independiente;30repeticiones instrumentadas por método, sin instalación/carga. Malla de parámetros prueba regímenes, no escalabilidad de datos porque problema es escalar fijo.
8. **Resultados/tablas/figuras.** results/ambiguity.csv144filas, ambiguity-runtime.csv60filas, JSON y ambiguity.png; notebook11celdas de código acumuladas ejecutadas secuencialmente IPython en proceso fresco, sin kernel/socket aislado. Máximo gap oráculo 2.665e-15;81mejoras estrictas63empates0peores frente a plug-in. Ancla α=λ=k=1,v∈[0,04;4]:

| Método | q | Peor regret social |
|---|---:|---:|
| Plug-in varianza media | 0.415808387049 | 0.078845294455 |
| Minimax regret | 0.353851617373 | 0.055577749247 |

Reducción ancla 29.510%. Barrido instrumentado6.7035s/picoPython218998bytes; tiempo no portable. Medianas robusto0.000977858s/14566bytes versus plug-in3.42115e-05s/833bytes. Coste adicional explícito. Figuras: regret frente a v (mecanismo/no dominancia puntual) y q frente amplitud (sensibilidad), ejes/unidades/escenario etiquetados.
9. **Análisis crítico/fallos.** Primera corrida falló umbral1e−8: boundedSciPy gap1,5446e−8 ante objetivo con kink; se mantuvo umbral y añadió refinamiento ternario independiente, sin cambiar parámetros ni conclusión. No ocultar esta adaptación exploratoria de implementación. Negativo: v=2,02 conocido favorece plug-in informado con regret0; robusto tiene regret positivo. Intervalo colapsado recupera30; k0 recuperaλ. Peor regret no equivale a peor pérdida absoluta.
10. **Limitaciones/sesgos.** LQ, α fijo, shock media0, varianza única fuente de ambigüedad, sin coste político/nombramiento creíble; datos sintéticos exactos; no inferencia, identificación, causalidad ni consejo de política. Uncertainty no estadística: no barras de confianza inventadas. No certificación de visualización en todos frontends. S2 componente mejorado con evidencia; programa S1, no S3 ni equivalencia M2.
11. **Comando exacto.** Desde carpeta inflation-bias-audit: `bash run.sh`. Crea venv, instala requirements fijadas y reproduce tests/lint/tipos/experimentos/notebook; requiere Python3.11+,PyPI. Resultados de timing varían. `python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v` desde raíz suite común.
12. **Referencias BibTeX.** referencias.bib contiene6entradas y URLs/DOI reales; alcance verificable en matriz. No se derivan conclusiones empíricas de artículos cuyo texto completo no fue auditado.
13. **Rúbricas1–5.** Original: novedad2,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP4. Ampliada:profundidadteórica4,aportedefendible3,calidadexperimental4,utilidad3,reproducibilidad4,honestidad5. Autoevaluación, no evaluación externa;2novedad refleja métodos clásicos.
14. **Siguiente iteración.** Definir contrato de datos con período/licencia e intervalo de varianza identificable; evaluar error en α manteniendo el mismo programa; luego modelar credibilidad del nombramiento. No prometer mejora real con incertidumbre arbitraria.

**Qué sabemos/construimos/podemos hacer:** ahora la misma herramienta distingue una elección puntual de una decisión robusta a intervalo explícito, calcula coste del compromiso y revela dónde fracasa dominancia. No sabemos si ese intervalo describe economía real.

**Checklist:** README,src,tests,benchmarks,resultsCSV/JSON/figura,notebookejecutado,config,requirementsfijadas,informe,MVP,6BibTeX,derivación,priorart,registro/roadmap presentes. Revisión independiente y publicación se registran aparte por coordinador; este informe no las simula.

**Revisión independiente31:** revisor científico reprodujo bash run.sh con exit0,12tests y11celdas; auditó derivación de extremos/monotonía/igualación y figura, sin bloqueantes en ese alcance. Dictamen consolidado en reviews/2026-10-31-cycle. CI remota se consulta por separado.


# Ciclo 1 de noviembre: intervalo estimado, calibración y fallo temporal

1. **Título y programa acumulativo.** La auditoría de transmisión monetaria conserva expectativas racionales (29), delegación (30) y varianza ambigua (31). Ahora pregunta cuándo los datos históricos permiten sustentar la garantía de regret. El incremento conecta inferencia con decisión; no pretende identificar una economía real.
2. **Hipótesis y aporte.** H1: el límite inferior Wilson al 95% de la cobertura gaussiana IID agrupada será ≥0,85, para confianza nominal 0,90. H2: habrá cero violaciones del bound, con tolerancia 1e−10, entre muestras cuyo intervalo contiene la varianza futura. Umbrales y diseño se fijaron en config antes de interpretar resultados. Clasificación: auditoría y adaptación de ingeniería de métodos clásicos. No se formuló una hipótesis de dominancia de pérdida promedio.
3. **Estado del arte.** La matriz prior-art1101.md verifica seis fuentes primarias pertinentes: NIST, SciPy chi², SciPy t, Wilson, Rogoff y Manski. referencias.bib conserva diez entradas acumuladas. Se distingue consulta de fórmulas/resúmenes/metadatos de lectura integral. No se acredita novedad disciplinar ni exhaustividad bibliográfica.
4. **Brecha y tres candidatas.** Usar datos macro reales tiene alta relevancia, pero faltan una definición identificable de shocks, licencia y medición de α. La ambigüedad conjunta α,v podría ampliar la herramienta, pero no se ha demostrado una reducción a extremos. Se elige auditar un intervalo estimado con generador explícito: reutiliza el solver, permite falsación y cierra un incremento verificable. La ausencia de identificación empírica permanece visible.
5. **Diseño y datos.** estimated-interval-config.json fija semillas 104729, 130363 y 155921; n=16,64,256; varianza histórica 0,25,1,4; 40 réplicas por semilla y celda; tres regímenes: normal IID, t5 IID y ruptura de varianza futura ×4. Son 3240 simulaciones y 362880 shocks históricos crudos en CSV.gz, con hash y versiones en JSON. La decisión usa t=1..n. Solo el evaluador conoce v futuro para calcular la pérdida esperada exacta; no hay ruido de simulación de evaluación. data-contract1101.md distingue estos fixtures del contrato empírico pendiente.
6. **Implementación y fórmulas.** src/variance_interval.py aporta una API tipada con dataclass inmutable; el runner conecta sus extremos con src/ambiguity.py. El intervalo conocido del ciclo31 se reemplaza por C(X), obtenido del pivote (n−1)s²/v~chi². derivacion1101.md y el notebook desarrollan la inversión paso a paso, unidades y supuestos. La intersección con [0,16] exige que la verdad esté en ese dominio; una intersección vacía produce abstención. En el evento v∈C(X), R(qR,v)≤sup(z∈C)R(qR,z). La probabilidad nominal de ese evento requiere normalidad IID y estabilidad hacia el futuro. No es una probabilidad posterior de v después de observar C. Las barras Wilson miden incertidumbre Monte Carlo de cobertura, una cantidad distinta.
7. **Tests y benchmarks ejecutados.** `bash run.sh` termina con exit0: 18 tests (seis nuevos y doce regresiones), Ruff y mypy sobre nueve archivos src. Cobertura medida del núcleo nuevo: 39/39 sentencias, 100%; acumulada:129/131, 98% redondeado. No se afirma cobertura de ramas. Se comprueban traslación, permutación y escala en veinte muestras, amplitud con confianza, cero, abstención, overflow y entradas inválidas. El oráculo de cuantiles usa gammaincinv: identidad distinta dentro de SciPy, sin independencia total de software. La suite común de economía pasa ocho tests por separado. El benchmark contiene 180 mediciones, treinta por tamaño y método; excluye instalación, importación y generación, y mide tiempo y pico Python, no RSS ni coste financiero real.
8. **Resultados y figuras.** Cobertura gaussiana IID agrupada: 0.90462963, intervalo Wilson95% [0.88565011,0.92074089]. H1 se cumple. H2 registra cero violaciones entre muestras cubiertas. estimated-interval.png contiene dos paneles inspeccionados: cobertura con Wilson frente a n y diferencia de regret medio. El notebook acumulativo tiene quince celdas de código ejecutadas desde el inicio mediante IPython en un proceso fresco; se guardan outputs, tablas y figuras. No se afirma ejecución mediante kernel aislado ni QA completa de frontend Jupyter.

| Régimen | n | Cobertura futura | Regret medio plug-in | Regret medio robusto | Violaciones del bound sin condicionar |
|---|---:|---:|---:|---:|---:|
|iid_gaussian|16|0.911111|0.00296466|0.00351167|32|
|iid_gaussian|64|0.900000|0.00081931|0.00079469|36|
|iid_gaussian|256|0.902778|0.00017939|0.00018187|35|
|iid_student_t5|16|0.800000|0.00572418|0.00483306|72|
|iid_student_t5|64|0.705556|0.00204000|0.00203409|106|
|iid_student_t5|256|0.680556|0.00062254|0.00062861|115|
|variance_break_x4|16|0.016667|0.10617334|0.07859189|354|
|variance_break_x4|64|0.000000|0.09893925|0.09214306|360|
|variance_break_x4|256|0.000000|0.09354652|0.09189236|360|

Cada punto agrupa 360 réplicas y tres varianzas. El oráculo informado tiene regret0 por definición, pero conoce v futuro: solo es una cota inferior. Plug-in y robusto utilizan la misma muestra, el mismo objetivo social y el dominio declarado. No hubo abstenciones en la malla; los tests cubren ese estado de la API.

| n | Método | Mediana segundos | Pico bytes Python |
|---|---|---:|---:|
|16|plugin|0.0000941|1776|
|16|interval_robust|0.0014719|16418|
|64|plugin|0.0000959|2544|
|64|interval_robust|0.0013063|16217|
|256|plugin|0.0000985|5752|
|256|interval_robust|0.0013414|17802|

9. **Análisis crítico y negativos.** Con t5 y la misma varianza, la cobertura cae de 0,80 a 0,70556 y 0,68056 al aumentar n. Bajo ruptura ×4 pasa de 0,01667 a cero para n64/256. La optimización sigue ejecutándose: robustez de optimización no repara un intervalo mal calibrado. Para normal IID con n16, el regret medio robusto 0,00351167 supera al plug-in 0,00296466; con n256 también hay un pequeño perjuicio. Se conservan esos resultados y todas las configuraciones. Las violaciones no condicionadas bajo normalidad son compatibles con confianza del 90%, que no significa garantía del 100%.
10. **Limitaciones, sesgos y madurez.** Los shocks son sintéticos con α=λ=k=1; no se estiman parámetros macro, dependencia serial ni credibilidad política. El supuesto externo v∈[0,16] no se aprende de los datos. El control temporal usa un DGP diseñado, no observaciones empíricas fuera de muestra. El componente sigue S2 y el programa S1; Monte Carlo no acredita S3 ni equivalencia con M2. No se añade otro lenguaje sin un cuello de cómputo demostrado; se conservan fórmulas, notebooks y motores anteriores.
11. **Comando exacto.** Desde inflation-bias-audit: `bash run.sh`. Requiere Python3.11+, venv y acceso a PyPI para las dependencias fijadas en requirements.txt; instala y reproduce código, tests, benchmarks y notebook. Desde la raíz, la suite común es `python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v`. Los tiempos dependen del host.
12. **Referencias BibTeX.** referencias.bib contiene diez entradas con URLs/DOI; prior-art1101.md registra seis fuentes pertinentes verificadas en este incremento y el alcance de la consulta. No se trasladan teoremas de elección de tratamientos a política monetaria.
13. **Rúbricas 1–5, autoevaluación.** Original: novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4. Ampliada: profundidad teórica4, aporte defendible3, calidad experimental4, utilidad4, reproducibilidad4, honestidad5. El aporte novedoso es modesto y estas valoraciones no sustituyen revisión externa.
14. **Siguiente iteración.** Contrastar un intervalo competitivo para no normalidad con supuestos de momentos y conjunto confirmatorio fijado; evaluar detección de cambios usando únicamente información disponible; después obtener una fuente macro con licencia y una definición identificable de shocks/α.

**Qué sabemos, construimos y podemos hacer ahora.** La herramienta transforma datos históricos en una decisión y separa cobertura estadística de garantía de optimización. Permite reproducir contraejemplos de colas y cambio temporal. Todavía no sabemos qué intervalo representa una economía real.

**Checklist de artefactos.** README, MVP, src, tests, benchmarks, CSV/JSON/PNG/CSV.gz, notebook ejecutado, config, dependencias fijadas, BibTeX, derivación, matriz de prior art, contrato de datos, informe14p y registro/roadmap presentes.

**Revisión independiente.** El revisor1101 reprodujo `bash run.sh` con exit0,18 tests y15 celdas de código. Inspeccionó la derivación pivotal, inversión, recorte y separación entre cobertura y bound; contrastó NIST y examinó los dos paneles. No encontró bloqueantes científicos dentro de ese alcance. Publicación y CI se informan por separado en el consolidado.
