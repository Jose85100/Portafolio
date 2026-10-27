# Ciclo de I+D+i — 27 de octubre de2026

## 1. Título
Funding Lead-Time Gate: activar fondeo comprometido antes de que llegue tarde.

## 2. Hipótesis y novedad incremental
Hipótesis falsable: dentro del menú y los3escenarios diseñados, existe un umbral que reduce brecha respecto a la regla reactiva2y cumple masa de brecha≤0,1, pagando costo explícito. Resultado: umbral6, masa0 frente0,5 y costo0,74 frente0,132. No es una mejora gratuita de beneficio; es compra de anticipación. Novedad local: plazo de desembolso, regla no anticipativa y reconciliación caja/deuda, frente a playbooks05/10que modelan caja/acciones pero no esta decisión.

## 3. Estado del arte
Baumol1952 estudia demanda transaccional de caja; Miller/Orr1966 analiza políticas de gestión de efectivo; no reproducimos sus soluciones analíticas. Holmström/Tirole1998 estudia oferta de liquidez privada/pública; sirve de marco, sin implicar garantía estatal aquí. Almeida/Campello/Weisbach2004 estudia restricciones financieras y ahorro de caja empírico; su evidencia no valida nuestro escenario sintético. Acharya/Almeida/Campello2013 relaciona riesgo agregado con elección caja/líneas: una línea cierta de nuestro modelo omite precisamente parte de ese riesgo.

Cinco referencias DOI/URL verificadas27oct mediante búsqueda de editores y registros institucionales. Se abrieron metadata yresumen original de Miller/Orr yregistro Illinois deAlmeida. Baumol redirigió con error yNBER devolvió403; se verificaron registros indexados de las fuentes originales, no lectura completa de artículos. No revisión exhaustiva ni prioridad científica.

## 4. Brecha y3ideas comparadas
Main e0cb173; PR84math/87riesgo/88micro abiertos al inicio, sin solape06. Más asignación/calendario repetiría26; demanda estocástica de pricing repetiría25; decisión de fondeo con leadtime ypasivo explícito cubre una brecha de18S1. Elegimos tercero. Se inspeccionaron motores05stress y10recovery: su foco es caja por escenario/ahorros por acción, no umbral observable con fondeo tardío. No se modifican contratos globales ni otros dominios.

## 5. Diseño y configuración
config.json: caja inicial8, monto de un giro8, comisión de solicitud0,5, interés simple2%por período sobre deuda efectivamente desembolsada, demora2, piso0. Horizonte5períodos arbitrarios; pesos0,5/0,3/0,2. Flujos netos: normal[−1,−1,1,1,1], burn sostenido[−2,−2,−2,−2,−2], burn adelantado[−4,−2,−1,−1,−1]. Todos sintéticos, unidades monetarias comunes. No tasa recomendada ni probabilidad estimada.

Menú: no solicitar, umbrales0/2/4/6/8. Se selecciona exante el menor costo esperado entre reglas con masa de brecha≤10%. La misma regla aplica a todos los caminos. El trigger observa caja al inicio después de fondeo pendiente; no observa el flujo corriente ni futuro. Solo se solicita si el fondeo llegará dentro del horizonte, conocido de antemano. Restricción a menú de reglas, no control óptimo global.

Orden de eventos: recepción pendiente→observación/solicitud→comisión y eventual fondeo lead0→control del piso→flujo neto e interés al cierre→control del piso. No se modela liquidez entre movimientos dentro del lote de cierre. El piso se comprueba también en estado inicial (período−1). Flujos futuros se usan solo para evaluar políticas, no para dispararlas.

## 6. Implementación y ecuaciones
src/funding.py implementa Facility validada, simulate, score y choose. Tipo Result registra caja/deuda/observación, solicitud, fondeo, primera brecha, costos yerror de identidad. Caja_t= caja previa+giro−comisión+flujo−interés; deuda_t=deuda previa+giro; interés=deuda desembolsada×tasa. Identidad parcial: caja−deuda=caja inicial+Σflujos−Σcostos. Principal no es ingreso ni beneficio y no se interpreta endingcash como rentabilidad. No amortización dentro del horizonte, y no tasa compuesta del principal.

Costo de política=esperanza de comisión e intereses, sujeto a masa de escenarios con al menos una brecha. No se asocia penalidad arbitraria monetaria a insolvencia. Si no hay regla factible, raiseValueError con recomendación de rediseñar; no se marca solución segura. ComplejidadO(KST), memoriaO(ST) por política materializada. Modelo de ledger de liquidez, no estados financieros IFRS/SFC.

## 7. Tests y mediciones
6tests pasan: identidad caja/deuda en leads0/1/2, oracle cerrado para solicitud fija0, prefijos iguales con futuros distintos (misma solicitud), activación tardía vs anticipada, lead0, estado inicial/fee/piso, ausencia de solicitud inútil fuera de horizonte, selección/costo0,74 yentradas inválidas/inviabilidad. Cobertura statements100% de80núcleo, no todo proyecto ni notebook. Ruffisolated y mypystrict pasan. No C++ ni sanitizers aplicables.

Benchmark6reglas×3caminos×5períodos: ~0,00085s y14248bytes picoPython con tracemalloc en corrida autor, valores últimos enJSON. Python3.12.14/Linuxx86_64. Escalabilidad medida duplicando los mismos escenarios y dividiendo sus pesos:3/30/300caminos,5repeticiones, medianas0,000061/0,000513/0,005527s; umbral6 y costo0,74 estables (diferencia<1e−10). Esto verifica tamaño computacional, no diversidad de escenarios ni evidencia adicional. No RSS ni garantía de latencia operacional. No semillas/MonteCarlo necesarios: enumeración determinista de escenarios; no se inventan intervalos estadísticos.

## 8. Resultados
| Umbral | Masa de brecha | Costo esperado |
|---:|---:|---:|
|No solicitar|0,5|0|
|0|0,5|0|
|2reactivo|0,5|0,132|
|4|0,3|0,362|
|6seleccionado|0|0,740|
|8|0|0,980|

La regla6paga0,608más que reactivo2y elimina0,5de masa dentro del conjunto. Regla8cuesta0,24más sin mejorar ese indicador. Con lead0se elige0ycuesta0,33; lead1elige4/costo0,442; lead2elige6/0,74; lead3elige8/0,82; lead4no tiene regla factible. No se traduce esa tabla a probabilidades de default reales.

CSVpreserva6reglas,30observaciones de trayectorias caja/deuda (2políticas×3escenarios×5períodos),5demoras; JSONincluye todos outcomes ystress externo. Figura ynotebook muestran cifras y curvas. Error de reconciliación <1e−10 en pruebas; no se cuenta un préstamo como ganancia.

## 9. Crítica y negativos
La anticipación cuesta ysolicita en camino normal un giro que resultará innecesario ex post: regla no sabe el futuro. No se compara con un oráculo que solo fondee caminos adversos. No solicitud tiene menor costo, pero viola presupuesto de riesgo. Con burnexterno[−4,−4,−4,−4,−4], la regla6falla: masa de brecha1en ese camino. Ese stress no está usado como validación estadística; muestra riesgo de especificación. La factibilidad desaparece con demora4. Los pesos elegidos pueden cambiar ranking; no hay prueba de robustez universal.

## 10. Límites y gobierno
La línea está comprometida y desembolsa con certeza; omite revocación, covenant, colateral, haircuts, costo de compromiso, vencimiento y amortización. Estos supuestos impiden uso como plan de fondeo real. No regula instituciones financieras ni recomienda cumplir norma alguna. Flujos sintéticos no identifican causalidad. El simulador continúa contablemente después de brecha solo para diagnóstico: no presume operación insolvente posible.

Debe validarse contrato, calendario de pagos/cobros, disponibilidad de líneas ybuffer con responsables reales antes de piloto. ComponenteS2 sintético, programa18S1no recertificado. Notebook realmente ejecutado IPython secuencial con namespace fresco ycaptura rich; noQA kernelJupyter. Figura PNGinspeccionada; interfaznotebook completa no inspeccionada. Entorno con paquetes científicos preexistentes; contenedor limpio adicional no probado.

## 11. Comando
Desde18-cfo-capital-liquidity-and-funding/funding-leadtime-gate: `bash run.sh` instala yreproduce. Autor: `REUSE_ENV=1 PYTHON="$PWD/.venv/bin/python" bash run.sh`. Dependencias directas fijadas, transitivas sinhash. RequierePython3.12 yacceso al índice para instalación; sinAPI ni credenciales.

## 12. Referencias BibTeX
Cinco entradas enreferencias.bib con DOIyURL. Cobertura ybloqueos se declaran en sección3. No se presenta resultado propio como evidencia de esos artículos.

## 13. Rúbrica autoevaluada
|Criterio|1–5|Motivo|
|---|---:|---|
|Novedad|2|Integración local de ideas clásicas|
|Rigor|4|Ledger, oracle yno anticipación; pocos escenarios|
|Reproducibilidad|4|Config/outputs/checks; freshcontainer pendiente|
|Código|4|Modular tipado yvalidado|
|Claridad|4|Lead, costo ypasivo explícitos|
|Impacto|3|Decisión CFO útil sintética|
|Honestidad|5|Costo yfallos fuera de diseño declarados|
|MVP|4|Pipelineejecutado; kernelQA pendiente|

## 14. Siguiente iteración
Siguiente iteración recomendada: validar la disponibilidad contractual del fondeo ymodelar vencimiento antes de ampliar políticas.
1.18-cfo-capital-liquidity-and-funding/funding-leadtime-gate: agregar repago yvencimiento con reconciliación.
2.10-crisis-management-recovery-planning: integrar acciones operativas que reduzcan burn cuando no hay umbral factible.
3.18-cfo-capital-liquidity-and-funding: comparar escenarios de revocación ydesembolso incierto con buffer de caja.

Checklist src✓ comando✓ tests✓ baseline✓ salidas/figura✓ notebookejecutado✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta18✓ madurezlocal✓. Revisor independiente reprodujo el comando completo con exit0 y revisó el núcleo sin bloqueantes. Publicación yrevisión registradas separadamente; no merge automático.
