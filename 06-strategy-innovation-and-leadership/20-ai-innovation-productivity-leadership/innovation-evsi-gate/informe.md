# Informe de I+D+i — 2026-10-23

## 1. Título
Innovation EVSI Gate: comprar evidencia antes de escalar una iniciativa IA.

## 2. Hipótesis y novedad incremental
H1: bajo el caso sintético configurado, seleccionar un piloto en el grid eleva el valor esperado neto al menos 1.000 unidades frente a decidir hoy. Resultado: +5.140,42; H1 se sostiene **dentro del modelo**. La contribución al repositorio es un gate beta-binomial exacto con costos, opción de no estudiar, auditoría MC y sensibilidad. No se reclama invención de EVSI ni prioridad científica.

## 3. Estado del arte
Chaloner y Verdinelli (1995) encuadran el diseño en utilidad esperada. Fleischhacker et al. (2023) desarrollan expresiones EVSI multinomiales que generalizan beta-binomial: es el antecedente más cercano, por lo que nuestro aporte es implementación/aplicación acotada. Heath et al. (2016) estudian aproximación por moment matching ante costos de simulación anidada; aquí la conjugación permite enumerar. Vervaart et al. (2021) aplican EVSI a extensión de ensayos, contexto más complejo no reproducido aquí. Safari et al. (2024, revisión2025) usan EVSI para desarrollo de modelos predictivos; no trasladamos su evidencia clínica a fintech.

Se verificaron títulos/autores/identificadores y resúmenes el 23-10-2026 en páginas originales arXiv, INFORMS y reporte CMU (URLs en referencias.bib). No fue una revisión exhaustiva ni lectura completa de todos los artículos; no se afirma benchmark contra sus algoritmos, que tienen alcances diferentes.

## 4. Brecha
Programa20 declara S1 y carecía de motor ejecutable. Los 15 motores previos incluyen asignación y opciones reales, pero no encontramos una enumeración exacta de estudio beta-binomial para decidir si comprar evidencia de desempeño IA. Este componente no sustituye el diseño causal del programa ni acredita el conjunto.

## 5. Diseño y config
Prior p~Beta(6,4), N=10.000 tareas futuras separadas del piloto, beneficio por éxito10, costo por tarea6 y fijo de rollout0. Todos son valores sintéticos en una unidad monetaria común. Piloto: fijo100 +5n. Grid n={0,10,25,50,100,200,500,1000}. Semilla20261023; 200.000 réplicas MC. No existen datos empresariales observados. Config y metadatos de Python/plataforma/versiones están guardados.

Utilidad U(p)=N(vp-c)-F; detener=0. K|p~Bin(n,p), posterior Beta(a+K,b+n-K). EVSI=E_K[max(0,U(E[p|K]))]-max(0,U(E[p])). Net value resta costo del estudio, que es cero para n=0. La política conoce K, no p latente. La muestra no consume la población futura ni aporta beneficio operativo; estudio y despliegue tienen presupuestos y horizontes separados, sin descuento. La alternativa fija usa el mismo posterior y payoff: solo cambia n.

## 6. Implementación
src/evsi.py: Case validado, PMF beta-binomial log-gamma normalizada, evaluate y choose. Costos finitos no negativos; priors/beneficio positivos; n entero no negativo. Normalizar no prueba por sí solo exactitud: se contrasta caso uniforme y oracle MC. Complejidad O(n) tiempo/memoria por diseño y O(sum n) sobre grid. Máximo log calculado una vez. Python tipado y núcleo sin dependencias externas; SciPy solo oracle de evaluación.

## 7. Tests y benchmarks
6 tests unitarios/invariantes pasan. Incluyen prior uniforme PMF=1/(n+1), EVSI(0)=0, no negatividad/monotonía sobre 12 priors y n0..20, no inferioridad frente a no estudio, piloto prohibitivo, acciones extremas, entradas inválidas y EVSI≤EVPI por cuadratura independiente en 3 priors con n0/10/100/1000. 100% cobertura de **46 statements del núcleo**, no del notebook ni total del proyecto. ruff src/tests/benchmarks y mypy src --strict pasan. No C++ ni sanitizers aplicables.

Escalabilidad observada (5 repeticiones, mediana; el hardware compartido introduce ruido): n100 ~0,00018s; n1000 ~0,00165s; n10000 ~0,02095s. Son mediciones de una corrida, no garantía de latencia. El grid completo con tracemalloc ~0,0467s y100.888 bytes pico Python; RSS~109.336KiB incluye intérprete y librerías, no es memoria exclusiva del algoritmo. results/summary.json y scaling.csv contienen valores exactos de la última corrida.

## 8. Resultados
| Política | n | Valor neto esperado | Coste estudio |
|---|---:|---:|---:|
| Decidir hoy |0|0,00|0,00|
| Piloto fijo |100|5.138,22|600,00|
| Grid EVSI |50|5.140,42|350,00|

EVSI bruto5.490,42, EVPI6.019,74. MC independiente por generación jerárquica produce5.153,61 con SE18,87, a0,70 errores estándar del valor enumerado. Es ruido de simulación bajo el modelo, no intervalo de ingresos reales. Los 200 bloques de1000 réplicas se guardan sin selección. Figura decision_curve.png inspeccionada visualmente: ejes/unidades/leyenda legibles y valores consistentes.

## 9. Análisis crítico y ablations negativas
El piloto fijo100 casi empata50: mejora2,19 unidades (<0,05%), por lo que no hay evidencia de ventaja material del selector frente a ese baseline. El beneficio es principalmente valorar estudiar frente a no comprar evidencia. Con costo variable0, elige1000 (mayor información). Con prior20 veces más fuerte y costo25, elige no estudiar. El test de fijo1.000.000 rechaza estudio: más datos pueden destruir valor neto. No hay identificación causal, prueba de eficacia real ni evidencia empírica externa. Priors equivocados invalidan optimalidad Bayes fuera de ese prior.

## 10. Limitaciones, sesgos y gobierno
Neutralidad al riesgo, beneficio y costos conocidos, una etapa y IID; no riesgo de cola, drift, efectos de red, dependencia, censura, sesgo de selección, negociación o daño a clientes. Un éxito operativo no equivale a efecto incremental de IA frente a control. Antes de uso empresarial: experimento aprobado, métrica causal, costos completos y horizonte descontado, guardrails, validación de prior y responsable de comité. Datos sintéticos sin PII/API. Kernel Jupyter TCP bloqueado por sockets; notebook ejecutado **realmente** en IPython secuencial en proceso, namespace fresco y captura de salidas. No se afirma validación de kernel. Cuerpo/tabla/figura y outputs guardados se inspeccionaron programáticamente; figura principal inspeccionada visualmente, no se realizó QA de interfaz Jupyter completa.

## 11. Comando exacto
Desde innovation-evsi-gate: `bash run.sh`. Se ejecutó con el entorno disponible mediante `REUSE_ENV=1 PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" bash run.sh`. README detalla Python3.12 e instalación de dependencias. No se validó instalación desde cero en segundo contenedor. Notebook: `python -m benchmarks.notebook`; modo kernel opcional `NOTEBOOK_KERNEL=1` en entorno que permita sockets.

## 12. Referencias BibTeX
Cinco entradas completas y URLs originales en referencias.bib. Registros bibliográficos verificados; cobertura de revisión limitada a resúmenes/metadata.

## 13. Rúbrica autoevaluada (1–5)
| Criterio | Nota | Motivo |
|---|---:|---|
| Novedad |2|Integración nueva local; método clásico|
| Rigor |4|Enumeración exacta y oracles; supuestos muy simplificados|
| Reproducibilidad |4|Semilla/versiones/outputs; kernel y fresh-install no verificados|
| Código |4|Modular tipado, tests y checks|
| Claridad |4|Unidades y decisión explícitas|
| Impacto |3|Decisión útil, datos sintéticos|
| Honestidad |5|Límites y casi empate declarados|
| MVP ejecutable |4|Corre completo en entorno disponible; kernel TCP no probado|

## 14. Siguiente iteración
Siguiente iteración recomendada: contrastar la recomendación con un diseño causal y costos de implementación reales aprobados.
1. 20-ai-innovation-productivity-leadership/innovation-evsi-gate: añadir payoff incremental frente a control con dos tasas desconocidas.
2. 19-ceo-fintech-business-strategy: evaluar sensibilidad al horizonte y descuento manteniendo unidades consistentes.
3. 20-ai-innovation-productivity-leadership/innovation-evsi-gate: reproducir notebook en kernel Jupyter en CI y validar prior con evidencia aprobada.

Estado: implementado y ejecutado; revisión independiente coordinada aparte; no publicado por el autor. S2 solo componente, programa20 S1. No producto operativo.
