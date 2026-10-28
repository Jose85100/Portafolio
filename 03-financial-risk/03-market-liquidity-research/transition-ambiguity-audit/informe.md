# CICLO28oct2026 — incertidumbre de transición de liquidez

## 1. Título
Banda de primera ruptura bajo ambigüedad rectangular de filas.

## 2. Hipótesis y novedad
Con caja6,H20, la cota superior supera nominal al menos5pp y reserva robusta mínima supera nominal al menos3unidades. Umbrales fijados antes de ejecutar. Nuevo alcance local: tratar matriz desconocida dentro de intervalos, frente a matriz fija del ciclo27. No se reivindica nuevo Bellman ni nueva teoría robusta.

## 3. Estado del arte
Cinco fuentes primarias verificadas28oct: Iyengar2005 sobre rectangularidad; Nilim/ElGhaoui2005 sobre transición incierta; Wiesemann/Kuhn/Rustem2013 sobre incertidumbre de parámetros; Grinstead/Snell sobre cadenas; BCBS2008 como contexto. ReferenciasBibTeX y alcance de lectura enprior-art. No se implementa inferencia estadística de esos trabajos ni se presupone vigencia regulatoria local.

## 4. Brecha y selección
Tres ideas comparadas: cuadratura adaptativa de factor, línea contingente de crédito y banda de matriz. Se elige tercera por tamaño mínimo y brecha explícita27. Main5b7d30e y PR abiertos[] al comenzar. BaselineforwardDP27 se carga sin modificar. No se altera motorC++ ni contrato global.

## 5. Diseño/config
Caja6,H20, flujos fijos(+1,−2), inicial(.8,.2), nominal q=(.05,.8). Intervalos por fila q0∈[.03,.07],q1∈[.7,.9], target5%.41reservas0..40. Inicial está fija; matrices ambiguas NO comparten necesariamente distribución estacionaria, media o marginales diarios. Estos intervalos son stress hipotético, no regiones de confianza calibradas. Se exploran cuatro esquinas estáticas como comparador dentro de un conjunto adaptativo másamplio.

## 6. Derivación y semántica
V_h(c,s) es riesgo de ruptura en próximos hflujos. Si h0,V=0; si c+g(s)<0,V=1; si h1 y caja posterior≥0,V=0. Para otro caso, sea c'=c+g(s). U_h(c,s)=max_{q∈[lo_s,hi_s]}[(1−q)U_{h−1}(c',0)+qU_{h−1}(c',1)]. L usa min y sus continuacionesinferiores. La expresión es afín enq: basta evaluar dos extremos, sin error de grilla sobreq. Se mezcla inicial fija(.8,.2). Cache por(h,c,s) limita cálculo. Naturaleza adapta en cada tiempo/caja/régimen: rectangularidad fuerte. No es por definición optimización sobre una sola matriz fija. Cada modelo estático admisible pertenece al conjunto rectangular, así que su riesgo está contenido en la banda, salvo precisiónflotante. Cotas de peorcaso dependen del conjunto supuesto, no de confianza estadística.

## 7. Tests y benchmark
Cinco tests: singleton vsforwardDP independiente sobre36combinaciones; contención de nueve matrices interiores/esquinas y conjuntos anidados; oráculo analítico2días; monotonicidad de reserva y ablaciónH1; entradasinválidas. Oráculo2días: desde caja0 y régimen normal, día1+1 sobrevive y día2estrés−2 rompe, así banda=q0=[.1,.4]. Cobertura realmente medida solo de modelo/adaptador, no experimento o kernelhermano. Ruff y mypyestricto de2archivos.41filasraw con estadosvisitados, tiempo y memoria. Sin MonteCarlo o benchmark largo: todo determinista. C++/sanitizers no aplican.

## 8. Resultados ejecutados
Caja6,H20: nominal0,25722510; banda[0,12504180;0,46053304]. Incremento superior−nominal20,3307943pp≥5pp. Reserva mínima22vs34, diferencia12≥3. Observación de esquinaestática máxima coincide con cota rectangular en esta configuración hasta≈1,11e−16. No se deduce equivalencia universal entre problemas. Error oráculo2días0. CurvasCSV y metricsJSON guardan cifras completas. La búsqueda inicial0..30 no alcanzaba objetivo robusto y devolvíaNone; se extendió0..40 por pérdida máxima20×2, conservando los umbrales originales. No se presenta una reserva inexistente en la rejilla original.

## 9. Crítica y ablaciones negativas
La complejidad del adversario adaptativo no aporta aumento observable sobre una esquina fija en este caso: reportado, no oculto. H1 elimina efecto de transición; singleton reproduce nominal. La banda es másancha por incertidumbre supuesta, no prueba error real de estimación. El cálculo mezcla cambios de persistencia y de marginales: no se etiqueta como comparación de marginales iguales del ciclo27. Curvas y resultados no garantizan que una entidad real necesite12unidades adicionales.

## 10. Limitaciones
Dosregímenes, flujos deterministas y matrices acotadas externamente. Sin aprendizaje, cobertura de intervalos, parámetros dependientes, estados ocultos, monedas, garantías de fondeo o política de activos. Si la matriz real sale del conjunto, no hay garantía. Rectangularidad puede ser conservadora respecto a una matriz fija desconocida; aquí no se identifica gap, sin prueba general de equivalencia. Exactitud solo del modelo finito a precisiónflotante, no riesgo empírico. Objetivo5% arbitrario, sin requerimientoLCR/NSFR/SFC.

## 11. Reproducir y entorno
`bash run.sh` instala y ejecuta. `SKIP_INSTALL=1` con entorno listo. Python3.12; versiones directas fijadas yvenv; transitivas sinlocktotal. Mantener hermano markov-first-breach-audit. Hashdelbaseline y plataforma enmetrics. Notebook con ejecución realIPython secuencial, outputs capturados, no fabricados. Figura inspeccionada separadamente; no se afirma renderHTML completo.

## 12. Referencias
Cinco entradas reales verificadas enreferencias.bib. Metadatos/resúmenes y fuentesoriginales, no revisión exhaustiva o lectura integral de artículos cerrados. No se atribuyen nuestros números a publicaciones.

## 13. Rúbrica
Autoevaluación: novedad2/5,rigor4,reproducibilidad4,código4,claridad4,impacto3,honestidad5,MVP4. Prototipo sintético de componente. Revisión independiente yPR solo se reportan con evidencia posterior; no se eleva todo el dominio.

## 14. Siguiente iteración
Siguiente iteración recomendada: construir intervalos de transición a partir de muestras temporales y separar su cobertura del cálculo robusto. Tareas: transition-ambiguity-audit validar región estadística; markov-first-breach-audit añadir incertidumbre del régimen inicial; laboratorio de liquidez modelar capacidad de fondeo antes de decisiones reales.

## Checklist
Código/comando/tests/baseline numérico/CSVJSONfigura/notebookejecutado/README/informe/cinco referencias/MVP/config/entorno presentes. No simular revisión, publicación o madurez operacional.
