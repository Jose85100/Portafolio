# CICLO30 — continuación del motor de salidas competidoras

## 1. Título
Calendario explícito e integración del descuento dentro del intervalo de default.

## 2. Hipótesis y novedad incremental
H preespecificada: descontar todos los defaults al cierre anual subestima más del2% la pérdida integrada con λd=.24/año, λp=1.2/año, ρ=.06/año, horizonte1año. Innovación incremental local: añadir contrato dimensional y eliminar aproximación temporal bajo intensidades/EAD constantes por tramo. No es una fórmula mundialmente nueva, estimador nuevo ni validación empírica. Se conserva íntegro el núcleo discreto29 y su semántica.

## 3. Estado del arte y atribución
Cinco referencias DOI en referencias.bib y matriz `benchmarks/prior-art.md`: Deng2000 motiva competencia hipotecaria; Putter2007, Austin2016 y Andersen2012 separan hazard e incidencia; FineGray1999 es un enfoque de regresión explícitamente NO implementado. Revisión focal de metadatos/abstracts, no exhaustiva ni lectura completa de textos restringidos. Las identidades supervivencia/incidencia son conocidas; nuestra integración de descuento es derivación elemental bajo supuestos, adaptada al motor local. No se atribuyen cifras propias a la bibliografía.

## 4. Brecha y tres alternativas
La iteración29 señalaba falta de calendario explícito. Se compararon integración temporal, ajuste empírico a cohortes y selección PD/prepago; elegida primera por verdad verificable y sin inventar datos. Decisiones/roadmap en research-log.md. Base0b2e582 contiene PR105; único PR abierto al inicio107 de coordinación. Cambios exclusivos dentro de la misma carpeta existente, sin duplicar producto ni tocar IFRS/shared.

## 5. Diseño y config
`benchmarks/calendar_config.json`: intensidades anuales .24/1.2, un año, EAD100 monetaria condicional, LGD.45, fuerza de descuento continua0/.06/.20 por año. 1,2,4,12,52,360 intervalos;18 escenarios exactos, sinMC. Datos sintéticos sin semilla porque no hay aleatoriedad; CPU/Python/plataforma en results/metrics.json, dependencias directas en requirements y entorno reproducible run.sh. Cada tramo puede tener intensidad/EAD propia, siempre constante dentro de ese tramo. No implica independencia de causas latentes identificables; el modelo especifica intensidades causa dadas activo.

## 6. Implementación, fórmula original y propuesta
`src/model.py` original: Dᵢ=Sᵢ₋₁dᵢ y pérdida al cierre; conserva probabilidades discretas suministradas. Nueva API `src/calendar.py`: duracionesΔ en años; intensidadesλd,λp y fuerzaρ en año⁻¹. k=λd+λp. ODE dS/du=−kS implica S(u)=Sᵢ₋₁exp(−ku), dᵢ=λd/k[1−exp(−kΔ)] y pᵢ análoga, con salida0 si k0. No convertir cada probabilidad por separado ni dividir PDanual entre12.

La pérdida exacta del tramo es Sᵢ₋₁EᵢL exp(−ρtᵢ₋₁) × λd/(k+ρ)[1−exp(−(k+ρ)Δ)]. Surge de integrar λd exp(−ku)exp(−ρu)du. El baseline usa exactamente la misma masaDᵢ y exp(−ρtᵢ). `integrated`, `exact` y `endpoint` corresponden a integral, término exacto y término al cierre. `expm1` evita cancelación con exponentes pequeños. El caso k+ρ0 da pérdida0 pues λd0. Derivación completa LaTeX y ecuación-código en calendar_notebook.ipynb. Tiempo/memoria O(H) nueva API; original conserva su diagnóstico O(H²).

## 7. Tests/benchmarks reales
11 tests:5 heredados y6 nuevos. Nuevos: fórmula cerrada, invariancia por partición y masa, negativos tasa0/hazard0, refinamiento, entradas inválidas y límitesLGD/overflow. Barrido determinista18casos, sin estimación de incertidumbre. Cobertura medida únicamente ambos núcleos85sentencias100%; no cobertura total del notebook ni del benchmark. Ruff y mypy estricto2núcleos pasan. No C/C++ modificado: CMake/sanitizers no aplican. No se añade lenguaje sin utilidad científica.

## 8. Resultados, tabla y figura
|Calendario, ρ=.06/año|Pérdida integrada|Pérdida al cierre|Sesgo relativo del cierre|
|---|---:|---:|---:|
|1 intervalo/año|5.593462846931|5.389757800769|−3.641841%|
|12 intervalos/año|5.593462846931|5.579211946515|−0.254778%|
|360 intervalos/año|5.593462846931|5.592996427253|−0.008339%|
H cumple>2% en el escenario preespecificado. Incidencia default.127178706886 y prepago.635893534432 se conservan al particionar. Diferencia exacta anual-mensual observada≈1.78e−15; no es error certificado universal. 18 filas crudas en results/calendar.csv, figura results/calendar.png, métricas en calendar_metrics.json. Ejecución inicial del barrido≈.037s y68308bytes tracemalloc, sensible al entorno; reproducción puede variar. No equivale a memoriaRSS ni coste de infraestructura. Original29 también se vuelve a ejecutar y conserva números.

## 9. Análisis crítico y negativos
Con ρ0, exacto y cierre coinciden: no hay ganancia temporal. Con λd0 pérdida0. Con tasas positivas, descuento al cierre es menor pues exp(−ρΔ)≤exp(−ρu) para u∈[0,Δ]. Esta desigualdad bajo supuestos no demuestra superioridad predictiva. Al refinar el calendario exacto es invariante solo si no se cambian funciones de intensidad/EAD. EADamortizable continua no se representa exactamente con valores constantes. El negativo29 de mismo default al primer bucket es de otra semántica discreta: no se lo reinterpreta como propiedad de intensidades continuas.

## 10. Limitaciones/sesgos
Intensidades suministradas, no calibradas, sin censura ni cohortes; no datos reales ni inferencia causal. Descuento continuo no es tasa efectiva anual sin conversiónρ=log(1+r), que el llamador debe hacer explícita. EAD condicional no incorpora ya supervivencia; no se modela variación dentro del tramo ni incertidumbre, recuperaciones, revolving o selección. El dominio puede incluir λ≥0 grandes, pero este pequeño prototipo no certifica exactitud para todo extremo de coma flotante. No cumple por sí solo IFRS9/SFC ni recomienda provisiones reales. Sin ampliación de madurez del programa; componente sintético verificado, no validado ni operacional, sin equivalencia automáticaS2/M2.

## 11. Comando exacto
Desde esta carpeta: `bash run.sh`. Instala versiones directas en .venv, ejecuta tests, cobertura, lint, tipos, ambos experimentos y ambos notebooks. Entorno ya listo: `SKIP_INSTALL=1 bash run.sh`. Notebook capturado de ejecución real IPython secuencial, validado nbformat; no se afirma ejecución de kernelZMQ ni renderHTML completo. Figura independiente inspeccionada visualmente. Transitivas sin lock completo, límite explícito.

## 12. Referencias BibTeX
`referencias.bib` conserva5entradas verificadas y matriz ampliada. Revalidación30: Wiley/PubMed para Putter y Deng; PubMed26858290 y22253319 para Austin y Andersen; editorial TaylorFrancis para FineGray. Referencias definen contexto/identidades, no nuestra tasa sintética ni recomendaciones bancarias. No promesa de prioridad mundial.

## 13. Rúbrica y artefactos
Autoevaluación1–5: novedad2, rigor4, reproducibilidad4, código4, claridad4, impacto3, honestidad5, MVP4. Checklist real: src tipado; tests; run.sh; config; requirements; instrucciones reproducibles de entorno;18CSV+JSON+figura; notebook29 y calendar_notebook ejecutados; README; MVP; informe14p;5refs; matrizpriorart; research-log/roadmap. Estado: implementado y ejecutado; revisión independiente y publicación se documentan al obtener dictamen/enlace. No afirmarCI completa verde sin verificar.

## 14. Próxima iteración
Siguiente iteración recomendada: mantener esta línea y añadir EAD continua sin cambiar las intensidades. Tres tareas concretas: `src/calendar.py` integrar EAD lineal por tramo; `tests/test_calendar.py` verificar invariancia con fechas irregulares; `benchmarks/calendar_config.json` definir origen/licencia y separación temporal antes de ajustar a datos reales. Criterios continuar/ajustar/cerrar en research-log.md.

## Evidencia de revisión independiente30
Revisor separado reprodujo `SKIP_INSTALL=1 bash run.sh` con exit0 y11tests; comprobó integral, unidades/año, duracionesaños, expm1, masas y comparadorfin con mismo calendario. Dictamen: sin bloqueantes del núcleo. Figura inspeccionada sin recorte; la revisión de PR/CI queda identificada por enlace al publicar y no equivale a validación externa.
