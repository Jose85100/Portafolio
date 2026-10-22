# Revisión integral de notebooks, modelos y usos

## Alcance y criterio de completitud

Se revisaron las cuatro carpetas de fraude, sus ocho notebooks, la arquitectura, el catálogo y el motor de pérdida. La ampliación desarrolla 304 celdas, 88 de código, 903 líneas ejecutables y 31 figuras. Cada notebook conserva datos, derivaciones, ajuste o cálculo del modelo, resultados, comprobaciones, usos y límites.

Completitud significa que el experimento se puede reproducir e interpretar de principio a fin bajo su alcance declarado. No significa que los detectores integrales estén validados para una cartera real. La adquisición de evidencia institucional, eficacia causal y operación durable permanecen fuera de estos experimentos.

## Qué cambió por área

| Área | Ampliación ejecutada | Uso y comprobación |
|---|---|---|
| KYC | Log loss, gradiente/Hessiano, dependencia parcial, confiabilidad y ajuste de odds | Comprobar escala probabilística y evitar duplicación de fuentes; diferencias finitas y casos extremos |
| Decisión | Umbral derivado, EVSI/EVPI, incertidumbre de eficacia y límite dual | Evaluar si nueva evidencia puede cambiar la acción; conciliar Bayes, límites de información y presupuesto |
| Red temporal | Ajuste individual y con red/interacción; maduración y campañas nuevas | Medir aporte incremental, falsos positivos en hubs y disponibilidad de la entidad actual |
| Cobertura de campañas | Valores marginales, escenarios, eficacia parcial y valor de información | Conciliar pérdida única y comparar MILP con enumeración; no sumar beneficios solapados |
| Ingresos | Pinball, cuantiles, conformal, modelo cero/monto positivo e intervalos por grupo | Separar ingreso corroborado de sospecha; publicar cobertura, ancho, cambio de régimen y discrepancia |
| Conciliación | Eventos únicos, transferencias internas, periodicidad, disponibilidad y abstención | Rechazar duplicados contradictorios; no convertir falta de escala o dato en una decisión numérica inventada |
| Tasas de proceso | Mezcla, contracción, beta-binomial ajustada y predictiva | Comparar grupos en test separado; distinguir varianza real de referencia demasiado estrecha |
| Monitoreo | Derivación de razón de verosimilitud, autocorrelación, múltiples canales y censura | Declarar horizonte de falsas alarmas; no atribuir causa ni ignorar demoras no observadas |

## Hallazgos que se conservan

- El nuevo modelo con red tiene AP **0,3186**, frente a **0,3292** del individual en su test temporal sintético. No se altera el test ni se presenta como una mejora. El generador incluye hubs legítimos y campañas nuevas; otra simulación o validación externa puede cambiar el resultado.
- El logit implementado con objetivo explícito concilia su gradiente con diferencias finitas: error máximo aproximado **1,66e−12** en el caso comprobado. Es una prueba local de cálculo, no una certificación general de optimización.
- La verificación informativa tiene valor neto supuesto de **14.290,50 COP** con prior 0,05, pérdida 2 millones y los parámetros de la prueba declarados. La prueba informa; no se le atribuye prevención directa adicional.
- El modelo de ingreso de dos partes cubre **89,6%** en una banda q0,1–q0,9 de su propio test. Su masa en cero puede volver conservadora la cobertura; no se compara como si fuera la misma población del experimento de boosting.
- La beta-binomial obtiene NLL predictivo medio **3,2774**, frente a **4,8174** de binomial. El mecanismo generador es beta-binomial y por eso la comparación favorece al modelo correctamente especificado. No es evidencia de superioridad universal.
- Con autocorrelación phi=0,85, mantener el umbral CUSUM independiente produce **79,5%** de réplicas con alguna falsa alarma a 120 días. En otro experimento de cinco canales independientes, reutilizar h individual da **28%**, frente a **4%** del umbral conjunto calibrado en otras réplicas. Son comparaciones de escenarios distintos; no se suman ni trasladan a una operación indefinida.

## Correcciones y aclaraciones de revisión

Se incorporó disponibilidad de la entidad actual al modelo de red: cuando el dato no está disponible, el conteo se codifica como cero con indicador explícito de ausencia. No se trata como cero observado. Se comprueba que las campañas de prueba por bloque no aparezcan en entrenamiento y que eventos futuros no cambien el pasado.

La guía de asignación ahora distingue el caso donde ordenar beneficios positivos es exacto —una acción, tiempos iguales y casos independientes— de menús, tiempos o pérdidas relacionadas que necesitan otra formulación. Las fichas separan sensibilidad de una prueba, eficacia de intervención y fricción monetaria.

El nuevo conciliador rechaza eventos contradictorios con el mismo ID, verifica invariancia a duplicados idénticos y traslados internos completos, y devuelve un estado de abstención cuando faltan referencia o escala. Su alcance es un pequeño experimento de datos, no un libro mayor institucional.

## Verificación y evidencia

Los ocho notebooks ejecutaron todo el código en procesos IPython independientes porque el host local bloquea sockets de kernels. Las salidas permanecen dentro de los archivos. [La evidencia](notebook-lab/execution_evidence.json) registra tamaños, métricas y hashes. Se verificaron esquemas nbformat, enlaces locales, consistencia de hashes, restricciones de modelos y figuras; las 16 figuras originales permanecen idénticas y se inspeccionaron las 15 nuevas.

El motor de pérdida conserva su suite de 21 pruebas y el workflow vuelve a ejecutarla junto a los notebooks con kernels Jupyter. La versión previa de la PR pasó ambos workflows; consultar el estado del nuevo commit antes de atribuirle esa validación remota. No se presenta esta revisión local como una aprobación formal independiente en GitHub.

## Qué requiere una cartera real

Etiquetas adjudicadas y maduras; semántica y calidad de fuentes; población elegible/rechazada; privacidad y acceso institucional; separación temporal por cliente/campaña; calibración independiente; medición causal o sensibilidad de eficacia; conciliación contable de pérdidas; pruebas de latencia y colas; monitoreo de drift; validación independiente. Se documentan como requisitos pendientes y no como capacidades ya implementadas.
