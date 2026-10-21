# 04 · Anomalías en el proceso de originación y canales

**S1 — diseño detallado.** Detección propuesta de desvíos en asesor, comercio, canal y secuencia de validación. Se investigan posibles omisiones, uso indebido de overrides o coordinación; también se detectan incidentes de datos y cambios legítimos. Una alerta agregada no acusa a un empleado ni prueba fraude de clientes.

## Hipótesis, unidades y cortes

Hipótesis: comparar cada grupo con su mezcla esperada de solicitudes y su régimen de política reduce falsas alarmas frente a tasas brutas. Dos unidades: evento/solicitud para secuencias y grupo-día o grupo-semana para tasas. El monitoreo usa solo lo disponible en cada cierre; nunca atribuye a originación una señal conocida después como si fuera preventiva.

Ejemplo ilustrativo: un canal eleva su aprobación mientras disminuye el registro de verificaciones. Podría ser una omisión de control, una nueva integración que cambió el logging o una campaña con solicitantes distintos. El análisis debe diferenciar esas explicaciones antes de abrir un caso de posible fraude.

## Variables

Secuencia de etapas, tiempo entre eventos, campos modificados después de verificación, overrides y su justificación, roles autorizados, cambios de política, versión del software, mezcla de producto/monto/canal y señales de calidad. Los resultados de fraude confirmado y primera cuota impaga llegan en cohortes posteriores; se usan como desenlaces y con su retraso explícito.

Registrar denominadores: solicitudes iniciadas, elegibles, verificadas, aprobadas y desembolsadas. Una caída de denominador puede elevar una tasa sin más eventos. Conciliar pérdidas de logging con conteos fuente antes de alertar. No utilizar tasa de default como etiqueta de fraude interno.

## Modelos

**Baseline:** tasas por grupo y período con intervalos binomiales y mínimos de exposición. Separar producto, política y campaña; no comparar un originador de microcrédito con uno de nómina sin ajuste.

**Ajuste por mezcla:** estimar en datos históricos `p_i=P(evento_de_control_i=1|X_i,politica_i)`. Para grupo `g`, obtener `E_g=sum_i p_i`, `O_g=sum_i y_i` y residuo aproximado `z_g=(O_g-E_g)/sqrt(sum_i p_i*(1-p_i)+epsilon)`. El evento es una omisión verificada o discrepancia operativa, no necesariamente fraude. La fórmula supone independencia aproximada; la implementación debe corregir sobredispersión y dependencia por lotes.

**Modelo jerárquico:** `logit(p_ig)=beta'X_i+u_g`, con `u_g~N(0,sigma²)`. La contracción parcial evita que pocos eventos conviertan a un grupo pequeño en el más extremo. Evaluar incertidumbre y no memorizar un efecto del grupo como única señal para grupos nuevos.

**Cambio secuencial:** CUSUM unilateral `S_t=max(0,S_(t-1)+z_t-k)` con alarma si `S_t>h`. Seleccionar `k,h` con simulación temporal de estabilidad y presupuesto de falsas alarmas; no interpretar cada cruce como una prueba independiente. Reinicio, período de espera y escalamiento deben quedar versionados.

**Secuencias:** transiciones de estados y conformidad frente a un flujo permitido por política. Score de rareza `-sum log(P(s_j|s_(j-1),contexto))`, con suavizado y ajuste por longitud. Comparar contra reglas de pasos obligatorios: una transición rara autorizada puede ser correcta, y una secuencia común puede esconder fraude. Un HMM es un challenger posterior si aporta sobre esos baselines.

## Etiquetas y experimentos

Separar tres desenlaces adjudicados: incidente técnico, incumplimiento de proceso y fraude confirmado. Las tres clases exigen acciones distintas. Conservar políticas legítimas vigentes por fecha y bitácora de cambios.

1. Simular grupos de distinto tamaño, productos y políticas; incorporar dependencia por lotes y estacionalidad semanal.
2. Introducir aumentos graduales de omisiones, saltos abruptos, overrides autorizados y fallos de logging.
3. Comparar tasas brutas, mezcla ajustada, jerárquico y CUSUM. Medir tasa de falsas alarmas por 100 grupos-semana y demora hasta detectar el cambio.
4. Para secuencias, comparar reglas, Markov y longitud normalizada. Evaluar eventos duplicados, fuera de orden y llegados tarde.
5. Revisar multiplicidad entre grupos: controlar presupuesto de alertas y estudiar procedimientos de descubrimientos falsos bajo sus supuestos. No afirmar control FDR si las pruebas secuenciales/dependientes no cumplen el procedimiento elegido.

Además de AP cuando haya etiquetas suficientes, reportar carga de casos, porcentaje de alertas explicadas por problemas técnicos, estabilidad ante mezcla y costos de revisión. Una detección tardía puede proteger originaciones futuras, pero no evita retroactivamente una pérdida desembolsada.

## Refutación y entregables

La hipótesis se debilita si las alertas desaparecen al controlar cambios de política o si el ranking solo refleja volumen bajo. El modelo no demuestra intención, colusión ni causalidad. Toda atribución requiere investigación de evidencia independiente y derecho de aclaración en el entorno institucional.

Entregables propuestos: taxonomía de eventos; simulador de proceso; reconstrucción temporal; baseline ajustado; notebook de falsas alarmas/demora; ficha de grupos nuevos y vista de evidencia por alerta. Pruebas: una política autorizada modifica el flujo permitido desde su vigencia; duplicar eventos no cambia conteos; ausencia de logging produce incidente de calidad; grupos con cero exposición no reciben tasa inventada.

Esta línea complementa los modelos individuales y de red. Integrarla exige deduplicar solicitudes y casos, limitar alertas por capacidad y conservar separado el motivo operativo del eventual hallazgo de fraude.

## Integración con motores y capas

Este especialista conserva estado S1. Su familia de señal se representa mediante una variable sintética en el [motor S2 de comparación y asignación](../loss-minimization-engine/README.md); ese experimento no implementa el detector especializado descrito arriba. Véanse [capas y contratos](../ARCHITECTURE.md) y [técnicas y función de pérdida](../MODEL_AND_LOSS_METHODS.md) para el desarrollo incremental y los criterios de comparación.

## Notebooks ejecutados: experimentos S2 acotados

- [Mezcla de cartera y contracción](notebooks/01-case-mix-and-shrinkage.ipynb)
- [CUSUM, falsas alarmas y demora](notebooks/02-cusum-false-alarms-and-delay.ipynb)

Los dos experimentos incluyen 40 celdas y cuatro figuras en conjunto. Usan datos sintéticos y no completan el detector especializado de esta ficha. Las ecuaciones y los resultados se desarrollan dentro de las celdas; las preguntas abiertas conservan estado de investigación.

[Agenda de investigación y ecuaciones adicionales](EQUATIONS_AND_RESEARCH.md) · [Reproducción y evidencia](../notebook-lab/README.md).
