# Auditoría30: escala externa, varianza y desviación estándar

##1 Título/pregunta
¿Puede la utilidad29 devolver SD física finita cuando la varianza no es representable? Decisión: continuar adaptador con unidad declarada; ajustar escala al rechazo; cerrar afirmaciones de superioridad general.

##2 Hipótesis/novedad
H: seis fixtures nominales e=frexp(unit)[1], n128/4096, unit1/1e200/1e-200, errorrelSD<=1e-12. Propuesta propia de contrato/composición, no identidad inédita. Tresideas comparadas y descarte en RESEARCH_LOG.md. Profundiza carpeta29; main0b2e582 y PR abiertos0 inspeccionados.

##3 Estado del arte
Matriz prior_art.md: Welford, Chan, Pébay, Higham, NumPy, Python. Seis referencias BibTeX reales, verificadas30 vía fuentes primarias(metadata editoriales y páginas oficiales). Reimplementación/adaptación: no prioridad mundial, sin búsqueda exhaustiva ni lectura integral de libros.

##4 Brecha acumulativa
29 usa M2 centrado: evita cancelación pero puede overflow/underflow con entradas finitas. Inf/0 en varianza no informa si SD aún es recuperable. NumPy+mismaescala es baseline fuerte del mismo problema; no comparar sólo contra variante deliberadamente débil.

##5 Diseño/configuración
config_scale.json: x=unit*(1+i mod4), tamaños128/4096, e nominal y deltas−1000,−400,0,400,1000 cuando e admisible[−1074,1023].42filas totales incluyendo cuatro métodos; ventanas malas se registran. Decimal80.from_float, sin datos empíricos ni causalidad. CPU/versions runtime en scale_summary.json. Dependencias directas fijadas, no lock transitivo.

##6 Derivación e implementación
Definir s=2^e>0, yi=xi/s. Entonces \bar x=s\bar y y
$$M_{2,x}=\sum_i(x_i-\bar x)^2=s^2\sum_i(y_i-\bar y)^2=s^2M_{2,y}.$$
Por tanto
$$V_{x,d}=2^{2e}M_{2,y}/(n-d),\quad SD_{x,d}=2^e\sqrt{M_{2,y}/(n-d)},\quad d\in\{0,1\}, n>d.$$
Varianza unidadesU²; SD unidadesU. src/scaled.py aplica ldexp, reutiliza src/moments.py29 intacto. EstadoO(1), tiempoO(n); escala externa, no aprendida del futuro. Ventana2^±400 conservadora; no cota universal de error ni condición necesaria matemática. Normalización rechaza fuera deventana; comprueba estadosfinito/M2no negativo. Float no certificado. status variance_overflow/underflow permite SD disponible; std_overflow deja ambasNone. n en fallo es prefijo procesado.

##7 Tests/benchmarks reales
bash run.sh exit0:8tests(4previos+4nuevos),50fixtures aleatorios×3escalas de propiedades adicionales, extremos1e±200, inputinválido/ddof y SDmuestraloverflow con±1.7e308. Cobertura: kernel29 35sentencias100%, wrapper43sentencias95%, combinado78sentencias97%; dos guardas defensivas no cubiertas. Ruff src/tests/scripts y mypy2núcleos pasan. C++/CMake/sanitizers no aplican; sin nuevo lenguaje ni cambioEL83. Revisor detectó stdldexp OverflowError sin capturar para ddof1; corregido y test de regresión añadido. No ocultar hallazgo.

##8 Resultados/tablas/figura

|Configuración nominal|Casos|Salida30|SDrelerror máximo|
|---|---:|---|---:|
|unit1|2|varianza y SD|<=1.78e-15|
|unit1e200|2|variance_overflow, SDfinita|<=1.78e-15|
|unit1e-200|2|variance_underflow, SDfinita|<=1.78e-15|

Seis casos pasan umbral1e-12. Kernel29 y NumPy sin escala:4/6 SD no finita o perdida. NumPy+mismaescala:6/6 SD disponible y error máximo1.11e-16, mejor que wrapper; resultado negativo importante. CSV42filas, resumenJSON y figura scale_audit.png inspeccionada. Figura disponibilidad por delta y error por unidad. Tiempos medianos5calls sintracemalloc; memoriaPython separada. NumPy normalizado incluye conversiónarray+ldexp dentro timing. Mantiene ventaja de velocidad; wrapper no presenta speedup. CSV guarda todoslosnúmeros y resultadosviejos29 se regeneran con mismo comando.

##9 Análisis crítico/ablaciones negativas
Quitar escala produceinf/0 devarianza; esto es limitación del rangofloat, no bugdeNumPy. La salidaSD cambia contrato y lo declara. Usar mismaescala enNumPy resuelveproblema y supera precisión/velocidad; valor agregado aquí es iterable sinarray y estados. Escalas desplazadas fallan ventana y no se eliminan delCSV. Mezcla1e±200rechazada y redondeo a1e16irrecuperable conservado en notebook. Sensibilidadno demuestra estabilidad universal.

##10 Limitaciones/sesgos
Fixtures deterministas periódicos, sólo6nominales y42filas; sin inferencia empírica. Escala externa, no universal ni selecciónautomática; ventana sacrifica rango mixto. Subnormales extremos y streams enormes no exhaustivos; noSD0garantizadoimposible fuera de fixtures. Constructor29 manualconfiado. Estadofailure puede no consumir resto deliterator; iteradores conefectoslaterales fuera alcance. MemoriaPython noRSS, NumPy nativa no totalmente visible. sin coste monetario ni validación operacional.

##11 Comando exacto
`cd 02-mathematics-statistics-and-quant/quant-libraries/streaming-moments && bash run.sh` desde raíz. Python3.12, pip/red para instalación. MATH_ENV=/ruta/venv opcional. Reproduce29 y30 con requisitosfijados. notebook_scale.ipynb ejecutado IPython namespace nuevo, outputsvisibles, sin afirmar kernelJupyterseparado.

##12 Referencias
referencias.bib6entradas, prior_art.md relaciona atribución y diferencia. fuentes.md conserva29, matriz/log30declaran nueva verificación. DOI artículospaywall solo metadata/abstract recuperados; no se afirma lectura completa.

##13 Rúbrica1–5
Autoevaluación no dictamenexterno: novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP5. Prototipo acotado verificado, nooperacional, no equivalenciaS2=M2.

##14 Siguiente iteración
Escaladinámica y mergeheterogéneo src/scaled.py; fixtures subnormales/mixed en tests/test_scaled.py; RSS y30reps en config_scale.json/results. RESEARCH_LOG.md mantiene gates y negativos acumulados; revisión independiente/publicación se identifican enPR, sinmerge automático.
