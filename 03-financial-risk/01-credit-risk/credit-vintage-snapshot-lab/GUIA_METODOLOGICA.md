# Guía metodológica: tarjeta y mora temprana

El objetivo es observar si una política de originación distingue cohortes o segmentos con distintos niveles de mora temprana. No hay datos de clientes incluidos: los resultados requieren extractos autorizados y reglas aceptadas por la entidad.

## Unidad, tiempo y evento

La unidad inicial es la cuenta identificada por `(id_credito, id_comercio)`; el cliente se identifica con `id_cliente`. La cohorte es el mes de originación `corte_origen`. El contrato de ejemplo toma los cortes MOB 1, 2 y 3, y define evento como **días de mora estrictamente mayores a 30** en cualquiera de ellos. Así, 30 días no es evento y 31 sí. Es distinto del uso habitual de «30+» como ≥30; confirmar la convención contractual antes de usar resultados.

Una cuenta es evaluable en MOB 3 si tiene una observación única y DPD conocido en cada MOB 1–3. La falta de una fila, el DPD nulo o una salida sin información posterior no significan que el cliente haya pagado: se reportan como no evaluables. Un corte mensual tampoco garantiza detectar mora que ocurrió y se curó entre cortes. Definir origen de MOB, fechas de corte, cancelaciones, castigos, migraciones y fecha de disponibilidad antes de la extracción.

## Métricas en número y saldo

Sea `E_i` la marca de evento, `M_i` la elegibilidad por maduración y `B_i` el saldo de capital observado en MOB 3. El denominador por número incluye cuentas elegibles y el de saldo solo cuentas elegibles con saldo conocido y no negativo:

\[
E_i=\mathbf{1}\left(\max_{m\in\{1,2,3\}} DPD_{i,m}>30\right),\quad
R_{\#}=\frac{\sum_i M_i E_i}{\sum_i M_i}.
\]

\[
R_{\$}=\frac{\sum_i M_i V_i B_i E_i}{\sum_i M_i V_i B_i},\qquad
V_i=\mathbf1(B_i\text{ observado y no negativo}).
\]

Reportar numeradores, denominadores y cobertura de saldo junto con las tasas. Si el denominador es cero, la tasa no está definida. El saldo en MOB 3 de cuentas con evento **no es pérdida**: no incorpora recuperaciones, castigos ni LGD. La elección de saldo de originación, primer evento o MOB 3 cambia la pregunta y requiere aprobación del dueño del indicador.

Para el nivel cliente, documentar identificación de personas, cuentas conjuntas, múltiples productos y cohortes. No atribuir un cliente a una única cohorte ni sumar saldos de cuentas con información incompleta sin una regla explícita. Reportar recuentos por cuenta y por cliente por separado.

## Segmentos y tiempos de decisión

| Corte | Variables admisibles | Pregunta |
|---|---|---|
| Originación | Tipo de persona, estrategia/TPV Experian, score y ubicación disponibles al aprobar. | ¿Qué tan bien discriminaba la política inicial? |
| Fin de MOB 1 o 2 | Las anteriores y avances efectivamente disponibles hasta ese corte. | ¿Qué riesgo posterior se observa al hacer seguimiento? |
| Cierre de MOB 3 | Trayectoria observada y primer avance. | ¿Cómo se distribuyó la mora temprana? Es descriptivo. |

Registrar si hubo avance, fecha, monto y primer MOB, respetando fecha de disponibilidad. Un avance posterior al primer evento no debe interpretarse como causa de esa mora. No decidir que un grupo es fraudulento a partir de un score o una anomalía.

## Perfiles, pruebas y validación

El análisis factorial múltiple puede combinar grupos de variables numéricas y categóricas mediante métodos apropiados para datos mixtos y balanceo por grupo. Ajustar preprocesamiento y factores en cohortes de entrenamiento; no incluir el objetivo ni el saldo en mora en la construcción de perfiles predictivos. Proyectar el resultado como variable suplementaria y verificar estabilidad fuera de tiempo. Evitar dar peso duplicado a variables muy relacionadas de avances.

Comparar perfiles con clustering para variables mixtas y criterios de estabilidad, tamaño mínimo e interpretación, sin fijar arbitrariamente un número de grupos. Para relaciones descriptivas utilizar tablas de contingencia, Cramér V, correspondencias múltiples, Kruskal–Wallis y Spearman según el tipo de dato; informar denominadores, intervalos, supuestos y comparaciones múltiples. Las asociaciones y valores SHAP no demuestran causalidad.

Modelos supervisados y anomalías requieren cohortes maduras, separación temporal y por cliente cuando corresponda, calibración, evaluación por segmentos y revisión de fuga temporal. Un score de anomalía prioriza investigación; no es una etiqueta de fraude. Supervivencia con avance como exposición requiere variable dependiente del tiempo y tratamiento explícito de censura y evento previo.

## Gobierno y reproducibilidad

Registrar fuente, esquema, fecha de extracción y disponibilidad, hash, versión de política, unidad monetaria, reglas de saldo y población. Las plantillas vacías solo verifican el flujo de ausencia de datos. Los ejemplos ilustrativos, si existen, se identifican como tales y no se mezclan con evidencia de cartera. No subir identificadores o información sensible al repositorio.
