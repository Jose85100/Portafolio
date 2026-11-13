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

## De la medición a la decisión

Los notebooks 07–11 convierten el EVER en decisiones. Cada método declara su supuesto de identificación; el memo final lo cita junto a la cifra.

**Puente a pérdida (07).** En cohortes con MOB 18 observado, $a=\Pr(C\mid E)$, $b=\Pr(C\mid \neg E)$, lift $a/b$ y captura $\Pr(E\mid C)$. Para una cosecha joven con tasa temprana $r$: $\widehat L=r a+(1-r)b$. Supuesto: $a$ y $b$ estables entre cosechas; se verifica por cohorte madura y se re-estima cuando cambian producto, política o cobranza. Las cancelaciones antes de MOB 18 son un evento competitivo, no un "sin castigo".

**Curva esperada y efecto de cohorte (07).** Bandas $\bar p_m\pm z\sqrt{\varphi\,\bar p_m(1-\bar p_m)/n}$ con sobredispersión $\varphi\ge1$ estimada en cohortes de referencia. Hazard logit en tiempo discreto, $\operatorname{logit}h_{i,m}=\alpha_m+\gamma_c+\beta^\top Z_{c+m}$. Como período = cohorte + edad, el modelo edad–período–cohorte libre no está identificado y la parte lineal de una serie de período se confunde con una tendencia de cohorte. El efecto de cohorte se reporta condicional a las covariables macro, y una tendencia suave de cohortes no se atribuye sin evidencia adicional.

**Mezcla frente a tasa (08).** $\Delta R=\sum_s(w_{1s}-w_{0s})\tfrac{r_{0s}+r_{1s}}2+\sum_s(r_{1s}-r_{0s})\tfrac{w_{0s}+w_{1s}}2$, exacta. Depende de la segmentación, por lo que se reporta con varias.

**Economía (08).** Margen ajustado = ingreso − costo − PD·LGD·EAD; PD de equilibrio = (ingreso − costo)/(LGD·EAD); RAROC sobre capital $\kappa B$. Valor de vida por cuenta: un bueno vale $Hm-b\,LGD\,B$; un malo, $(1-a)Hm+a(\tau m-LGD\,B)-k$. La **tasa de malos de equilibrio** $\bar g/(\bar g+\bar\ell)$ indica si una banda crea o destruye valor. Con aprobados solo se evalúa **endurecer** el corte.

**Score, TPV y rechazados (09).** AUC, Gini, KS y orden por bandas sobre aprobados (truncados por el corte); PSI sobre solicitantes para cambio de población. Aporte del TPV: ΔAUC fuera de tiempo con bootstrap pareado. Swap set entre política vigente y alternativa. Inferencia de rechazados: si la aprobación es una regla sobre variables observadas, la selección es ignorable dado esas variables y un modelo ajustado en aprobados es válido cerca del soporte. Con una regla determinística todo rechazado queda fuera del soporte en alguna variable, así que se reporta la distancia. El bureau retro por bandas es un contraste simple y sesgado; los *overrides* manuales rompen el supuesto. La evidencia definitiva es una muestra controlada.

**Avance: señal o causa (10).** El landmark en MOB 1 con Mantel-Haenszel ordena el tiempo, pero no elimina la selección por estrés no observado. Diferencias en diferencias sobre un cambio de política, con tendencias paralelas revisadas por cohorte, errores agrupados por cohorte y la advertencia de pocos clusters; primera etapa y cociente de Wald para el efecto por avance evitado. RD local lineal con kernel triangular en umbrales que cambian un tratamiento **entre aprobados** (cupo); no en el umbral de aprobación, donde no hay desempeño debajo del corte.

**Prueba controlada (11).** Tamaño para dos proporciones con potencia 80 % y α 5 %, efecto de diseño si se asigna por grupos, métrica en el MOB donde actúa el mecanismo, guardarraíles y regla de detención. Para el swap-in, una prueba de precisión con su costo de información. Asignación por hash con sal registrada y balance por diferencias estandarizadas. Toda cifra del memo cita su supuesto.

## Benchmark de mercado (12)

Los datos públicos de la SFC son de **stock** (saldo y mora al corte) y **flujo** (compras, avances, castigos, desembolsos); no hay cosechas públicas. Definiciones: $ICV_k$ = saldo con mora mayor a $k$ días / saldo, con la cartera de consumo vencida a partir de 30 días; tasa de castigo = castigos de capital de 12 meses / saldo promedio de 12 meses, solo con 12 meses consecutivos; **mora ajustada** = (mora >30 + castigos 12 m) / (saldo + castigos 12 m), que evita premiar a quien castiga rápido.

Controles: llave por código SFC y no por nombre (fusiones y marcas nuevas); conciliación del saldo entre el formato de tarjetas (incluye empresariales) y la distribución de cartera (solo consumo); cuadre vigente + vencido = saldo. Se comparan solo emisores con cartera de consumo comparable.

Cosecha y stock se relacionan por $S=\sum_a w_a\sum_{k\le a}e_k(1-\rho)^{a-k}/\sum_a w_a$, con $e_k$ la entrada a mora a la edad $k$, $\rho$ la salida mensual de la mora (castigo o cura) y $w_a=(1+g)^{-a}$ el peso de las cosechas cuando la originación crece a tasa $g$. El crecimiento pesa más las cosechas jóvenes: baja el stock si la mora por edad sube con la edad (salida lenta) y lo sube si la mora entra temprano y sale rápido. La hipótesis inicial de que crecer siempre diluye la mora resultó falsa; por eso el benchmark de stock no reemplaza la comparación de curvas. El contraste con el buró (TransUnion, mora 60+ por saldo) valida dirección y orden de magnitud: universo y definiciones difieren.

## Gobierno y reproducibilidad

Registrar fuente, esquema, fecha de extracción y disponibilidad, hash, versión de política, unidad monetaria, reglas de saldo y población. Las plantillas vacías solo verifican el flujo de ausencia de datos. Los ejemplos ilustrativos, si existen, se identifican como tales y no se mezclan con evidencia de cartera. No subir identificadores o información sensible al repositorio.
