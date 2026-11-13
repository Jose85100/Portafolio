# Ciclo de I+D+i — 26 de octubre de2026

## 1. Título
Dependency Schedule Gate: transformar un presupuesto de iniciativas en un calendario ejecutable.

## 2. Hipótesis y novedad incremental
Hipótesis inicial de trabajo: mejorar NPV al menos0,5 frente a una prioridad por margen/costo. **Refutada** en el caso base: ambos dan11,655966. El contrato implementado exige no inferioridad del exacto frente al baseline factible. Sensibilidad incluye beneficios habilitados mayores, sin borrar el resultado negativo. Contribución local: certificar en una instancia pequeña precedencias de terminación y caja/capacidad por período. No se inventa project scheduling ni NPV.

## 3. Estado del arte y cobertura
Pritsker/Watters/Wolfe1969 formulan programación binaria de múltiples proyectos; Russell1970 conecta calendario y valor presente. Brucker etal1999 clasifican recursos/precedencias/objetivos. Hartmann/Briskorn2010 revisan variantes, incluidos objetivos NPV y proyectos múltiples. Kolisch/Sprecher1997 presentan PSPLIB como referencia de benchmarking. No ejecutamos instancias PSPLIB ni comparamos rendimiento con métodos de literatura: esto es un MVP sintético, no un algoritmo de frontera.

Cinco entradas DOI/URL en referencias.bib. Verificación26oct: búsquedas de páginas originales de editores, PDF institucional del autor Hartmann y registro institucional TUM de Kolisch. ScienceDirect directo devolvió403; INFORMS devolvió navegación parcial. Se verificaron metadata y resúmenes, no se leyó íntegramente toda literatura. PDF de Hartmann confirmó título/autores/DOI y alcance. No revisión exhaustiva.

## 4. Brecha y comparación de3ideas
Main674699d contenía cursos matemáticos nuevos; único PRabierto83 documentaba riesgo y no se solapaba. Motores04/15 ya seleccionan proyectos con pertenencia de prerequisitos, no calendario de terminación. Se compararon: robustez de capital por escenarios (próxima al ejeEVSI23/24); lag de pricing (repetiría25); calendario con presupuestos y recursos renovables (brecha diferenciada). Se eligió tercero en15-enterprise-transformation-portfolio/dependency-schedule-gate. No se alteran contratos globales ni motores previos.

## 5. Modelo y configuración
Cinco proyectos opcionales: platform(costo4,beneficio0,duración2,personas1), analytics(3,14,1,1) yautomation(3,9,1,1) requieren platform; standalone(5,10,1,2); controls(2,1,1,1). Horizonte4, caja disponible8por período, personas2. Inicio entero t, pago costo en t y beneficio único en t+d. Beneficio0de platform significa solo habilitador; sus descendientes no pueden empezar hasta que finalice. Todo es sintético, una unidad monetaria común y período arbitrario. Descuento0,1por período, no recomendación financiera.

ObjetivoΣseleccionados[b_j/(1+r)^(s_j+d_j)−c_j/(1+r)^s_j]. Restricciones: fin≤horizonte; cada dependencia seleccionada y terminada antes de s_j; gastos iniciales en cada t≤presupuesto_t; personas ocupadas durante[s_j,s_j+d_j)≤capacidad. Se permite rechazar proyectos y selección vacía0. Presupuesto **expira**, no se acumula ni se repone con beneficios; esto es disponibilidad de financiación, no un balance de caja modelado. Duraciones deterministas y no preemptivas. No hace falta seed: cálculo completamente determinista.

## 6. Implementación
src/schedule.py valida nombres, unidades, DAG sin ciclos, finitud, capacidades y duraciones enteras positivas. exact enumera fecha o exclusión y verifica restricciones; greedy usa misma instancia y evaluador, prioridad(margen/costo), omite proyectos negativos sin dependientes y respeta calendario. Retiene plataforma habilitadora aunque su NPVindividual sea negativo. Límite1–8proyectos y2millones de combinaciones; producto finito comprobado antes de enumerar. Núcleo stdlib tipado con Outcome. Complejidad exponencial en proyectos y horizonte; no se oculta como producto escalable.

## 7. Tests y benchmark
7tests automatizados pasan. Incluyen precedencias de terminación, dependencia omitida, límites de caja/capacidad, fechas inválidas, caso analítico de un proyecto, stop, monotonicidad de capacidad y no inferioridad exacta, DAGinválido y guardia de enumeración. Oracle independienteMILP en3proyectos: binarias proyecto/inicio, desigualdades por período y precedencia por ventana de inicio; objetivo coincide a8decimales con enumeración. SciPy solo se usa para el oracle. No C++ ni sanitizers aplicables.

Cobertura statements100% de81del núcleo; no de plotting/notebook ni repositorio entero. Ruffisolated y mypystrict pasan. Benchmark base evalúa2500combinaciones, con tracemalloc ~0,074s y2424bytes picoPython en corrida autor inicial; última cifra en summary.json. Medición de sensibilidad sin tracemalloc:162,768,2500,6480candidatos para horizontes2..5, aproximadamente0,0004..0,035s. No se midió RSS ni se certifica SLA. Python3.12.14/Linuxx86_64 en metadatos; paquetes directos fijados. La precisión óptima es combinatoria finita bajo tolerancia1e−10 de comparación, no teorema empresarial.

## 8. Resultados ejecutados
Caso inicial exacto y greedy: standalone inicia0(fin1), platform1(fin3), analytics3(fin4), automation3(fin4), controls omitido. NPV11,655966. Usos de personas por período:2,1,1,2, caja inicial5,4,0,6; todas restricciones satisfechas. No mejora numérica sobre greedy en este caso.

| Beneficio analytics | NPVexacto | NPVgreedy | Diferencia | Inicio platform exacto |
|---:|---:|---:|---:|---:|
|14|11,655966|11,655966|0|1|
|20|15,903012|15,754047|0,148965|0|
|30|23,416160|22,584181|0,831979|0|

Relajación de dependencias: NPV18,628099, analytics/automation inician0sin plataforma; infeasible bajo contrato original. Es una cota optimista y ablation negativa, nunca una propuesta de ejecución. Sensibilidad personas1/horizonte4 produce7,932245; personas3/horizonte4 produce12,040571. Aumentar personas no calcula costo de contratación.

CSV conserva calendarios elegidos,12escenarios horizonte/capacidad y3valores habilitados; JSONincluye baseline/cota/recursos medidos; figura Gantt comparativa y notebook tienen outputs. No hay MonteCarlo ni datos de compañías; no se inventa incertidumbre estadística para resultados deterministas.

## 9. Crítica, fallos y ablations
Se evitó baseline engañoso que financiara controls de valor negativo: al fortalecerlo, la mejora inicial desaparece. Ese resultado se mantiene y la hipótesis+.5se declara refutada. Beneficios mayores sí cambian el orden, pero los3casos no constituyen una evaluación amplia de heurísticas. Exacto es lento por diseño; seis mil candidatos son pocos. La cota sin dependencias muestra por qué financiar no prueba ejecutabilidad; no es comparación justa como política alternativa. No extrapolar diferencias a compañías ni afirmar impacto real.

## 10. Limitaciones y gobierno
No retrasos aleatorios, presupuesto acumulado, incertidumbre de beneficio, salarios recurrentes, cobros parciales, inflación, regulación, riesgo de ejecución o decisiones secuenciales. controls es nombre sintético opcional: **no representa una obligación legal ni un control requerido**. Un caso empresarial real debe marcar proyectos obligatorios fuera de esta selección opcional o ampliar contrato; no usar el motor para omitir controles necesarios. Valores no causales. Datos sinPII ni APIs.

Componente S2 sintético, programa15 no se recertifica. Notebook se ejecuta realmente enIPython en proceso, namespace fresco youtputs rich; no se afirma QA de kernelJupyter. PNG inspeccionado: barras/fechas/NPV legibles ycalendarios coinciden. Interfaznotebook completa no inspeccionada. Entorno con paquetes científicos preexistentes; freshcontainer no probado. Revisor independiente reprodujo el comando completo con exit0; revisó el núcleo y no encontró bloqueantes.

## 11. Comando exacto
Desde15-enterprise-transformation-portfolio/dependency-schedule-gate: `bash run.sh` creaentorno/instala/reproduce. Ejecución autor: `REUSE_ENV=1 PYTHON="$PWD/.venv/bin/python" bash run.sh`. Dependencias directas enrequirements.txt; transitivas sinhash. RequierePython3.12 yacceso a índice para instalación. `python -m benchmarks.run` y `python -m benchmarks.notebook` regeneran salidas.

## 12. Referencias BibTeX
Cinco entradas verificadas enreferencias.bib; cobertura y403de editores explícitos en sección3. Ningún resultado afirma reproducción de PSPLIB.

## 13. Rúbrica autoevaluada
| Criterio | Nota1–5 | Justificación |
|---|---:|---|
|Novedad|2|Integración nueva local de métodos conocidos|
|Rigor|4|Enumeración yMILP independiente; datos muy pequeños|
|Reproducibilidad|4|Config/outputs/checks; freshcontainer pendiente|
|Código|4|Contratos validados ytipos|
|Claridad|4|Pagos/cobros/precedencias explícitos|
|Impacto|3|Decisión ejecutiva sintética|
|Honestidad|5|Hipótesis refutada ybaseline fortalecido|
|MVP|4|Completo en entorno; kernelQA pendiente|

## 14. Siguiente iteración
Siguiente iteración recomendada: contrastar el modelo pequeño contra casos públicos de mayor tamaño sin perder restricciones de negocio.
1.15-enterprise-transformation-portfolio/dependency-schedule-gate: agregar proyectos obligatorios y caja acumulada con pagos parciales.
2.15-enterprise-transformation-portfolio: evaluar datos aprobados de disponibilidad yduraciones, separar estimación yplanificación.
3.04-data-investment-prioritization: conectar selección estática ycertificado de calendario, mostrando brecha entre financiar ycumplir plazos.

Checklist: src✓ comando✓ tests✓ baseline✓ salidas✓ figura✓ notebookejecutado✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta15✓ madurezlocal✓. No merge automático; publicación yrevisión se registran separadas de implementación.
