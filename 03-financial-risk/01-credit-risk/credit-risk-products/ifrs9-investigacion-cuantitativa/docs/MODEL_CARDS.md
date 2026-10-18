# Catálogo y fichas de modelo

Todos los modelos están implementados, pero su evidencia es **sintética**. Ajustado significa estimado en el entrenamiento del experimento; no calibrado con cartera colombiana. Las restricciones [0,1] son un contrato deliberadamente acotado: productos con pérdidas, costos o disposiciones fuera de ese rango requieren otra interfaz.

## PD-L1 · Logit a 12 meses

- **Objetivo:** default en 12 meses por contrato con horizonte maduro.
- **Entradas:** score (mayor = menor riesgo), segmento binario, factor macro estandarizado observable al origen. No usa saldo al default.
- **Estimador:** regresión logística regularizada L2, C=1; sin class weighting para no distorsionar probabilidades sin recalibración.
- **Curva:** p12=σ(βX+γM); hazard mensual h=1−(1−p12)^(1/12). Macro cambia log-odds a cada mes; más allá de 12m es extrapolación, no calibración lifetime.
- **Validación:** AUC, Brier, log-loss, tasa media, calibración y contraste pareado en OOT.
- **Fallas:** duración ignorada, cambios estructurales, covariables omitidas; ventana incompleta no admisible como etiqueta cero.

## PD-S1 · Supervivencia discreta mensual

- **Objetivo:** hazard de primer default condicionado a estar vivo al inicio del intervalo.
- **Entradas:** mismas características más log(1+edad)/4. Una fila por mes en riesgo; default sólo en fila terminal; meses consecutivos.
- **Estimador:** pooled logistic L2, C=1; no son efectos de duración libres por mes ni un Cox continuo.
- **Curva:** q_m=h_m∏_{j<m}(1−h_j). Censura administrativa deja de aportar filas sin inventar un default futuro.
- **Validación:** score a 12 meses, supervivencia, conservación de masas, sensibilidad de edad/macro. La validación de vida a 36 meses sigue pendiente con datos apropiados.
- **Fallas:** censura informativa, covariables posteriores al corte, correlación serial al estimar incertidumbre. No se reportan errores estándar ingenuos por fila.

## PD-M1 · Transiciones de rating

- **Objetivo:** flujo mensual desde tres ratings vivos al cuarto estado de default absorbente.
- **Estimador:** frecuencias de transición con pseudoconteo .5 por destino en filas vivas. La fila default es exactamente absorbente. Si smoothing=0 y falta una fila viva se rechaza el ajuste.
- **Escenario:** shift de log-odds de default con beta macro=.35 suministrado; conserva la composición relativa de los destinos vivos y la suma de filas. No es un coeficiente estimado en este panel.
- **Validación:** ejemplo geométrico de dos estados, masa no negativa, OOT por rating y sensibilidad de suavizado.
- **Fallas:** homogeneidad, Markov de primer orden, pocos defaults; ratings del generador no representan exactamente el generador de default. Su mala calibración es visible, no se oculta.

## LGD-W1 · Media de workout por segmento

- **Objetivo:** promedio por contrato de pérdidas descontadas a default en casos cerrados, separado por segmento.
- **Entradas:** segmento y loss_fraction. Desconocidos o segmentos ausentes se rechazan.
- **Uso:** baseline transparente para severidad; no responde a macro ni garantía individual.
- **Fallas:** sesgo por cierre, heterogeneidad y dependencia residual con exposición. La media por contrato difiere de una tasa agregada ponderada por exposición; la elección está documentada, no son intercambiables.

## LGD-F1 · Logit fraccional

- **Objetivo:** media de loss_fraction ∈[0,1].
- **Entradas:** garantía/EAD supuesta a default, segmento y macro. Las features se estandarizan con medias y desviaciones sólo del entrenamiento.
- **Estimador:** cuasiverosimilitud Bernoulli media + penalización .01 sobre coeficientes sin penalizar intercepto; L-BFGS-B con gradiente analítico. Admite targets 0 y 1; no se aplica una beta a endpoints.
- **Validación:** MAE, RMSE y sesgo en workouts posteriores reservados; no implica calibración sobre recuperaciones abiertas.
- **Fallas:** forma funcional, dependencia con EAD, shift de garantía, selección de casos cerrados. No estima distribución completa ni intervalos de coeficientes.

## LGD-C1 · Flujos de recuperación

- **Objetivo:** 1−PV(recuperaciones netas a default)/EAD, acotada a [0,1].
- **Supuestos:** haircut garantía 25%, costo como haircut adicional 8%, recuperación no garantizada 15% sobre residual; recuperaciones en años 1/2/3 con pesos .5/.3/.2. Son parámetros, no ajustes estimados.
- **Escenario:** el valor realizable de la garantía se escala por exp(−.12×macro), con límite a recuperación total. El ratio garantía/EAD se asume constante por mes: no es una tasación proyectada con amortización endógena.
- **Descuento:** EIR anual efectiva del préstamo. Recuperaciones a default, antes de descuento a reporte.
- **Fallas:** garantías sin calendario jurídico/costos, relación dinámica colateral/saldo, cashflows negativos netos, recuperaciones superiores al EAD. El piso oculta superávit en esta interfaz acotada; Stage 3 heredado sí expone superávit.

## EAD-A1 · Amortización contractual

- Anualidad de tasa anual efectiva y cuota constante. EAD al inicio del mes: el último mes conserva saldo antes de su pago, evitando omitir default en el último intervalo.
- Tasa cero usa balance/plazo. Después de vencimiento EAD=0. Cupón contractual y EIR de descuento son entradas distintas.
- No incluye mora acumulada, fees, nuevo desembolso ni modificaciones. No usa saldos observados futuros.

## EAD-P1 · Prepago independiente

- EAD contractual multiplicada por (1−CPR)^((m−1)/12), con CPR anual de referencia 12%.
- Interpreta prepago total independiente de default; es exposición esperada por prepago, no hazard de default.
- Si prepago depende de riesgo, reemplazar por riesgos competitivos; no multiplicar además por otra supervivencia de prepago.

## EAD-C1 · CCF fijo y fraccional

- Revolver baseline: CCF=.5. Challenger: logit fraccional de utilización, segmento y macro en ventanas completas de default.
- Target CCF=(EAD_realizada−saldo_corte)/no_utilizado_corte; requiere no utilizado positivo y target admisible. El generador entrega targets ya construidos, no una extracción de snapshots.
- EAD=saldo+CCF×(límite−saldo), hasta vida contractual del cupo. Nunca sobrepasa límite bajo este contrato acotado.
- Se informa MAE/RMSE/sesgo de CCF en ventanas reservadas; aún falta backtest monetario por horizonte con cambios de límite y sobregiro.

## S3-CF · Activos financiados deteriorados

- No usa PD de default futuro. Base: saldo bruto financiado menos PV de flujos netos esperados desde reporte; piso cero visible como decisión del laboratorio.
- Cada escenario puede multiplicar recuperaciones y retrasarlas. Los flujos deben existir explícitamente; no se imputan desde un score.
- La vida de recuperación puede superar la vida contractual remanente. No se trunca al mes 12 ni se usa CCF de disposiciones futuras.
- No incluye POCI, modificaciones, interés sobre importe neto, curas ni asientos.

## PM-LR · Matriz lifetime simplificada

- Universo separado: cuentas por cobrar con buckets mutuamente excluyentes; elegibilidad contable no resuelta por el algoritmo.
- Ajusta sum(shortfall_PV)/sum(exposure) por bucket con cohortes completas; escenarios multiplican tasas y se ponderan a nivel ECL.
- No estima PD/LGD/EAD separadas; no sumar sus resultados al motor por componentes para los mismos instrumentos.
- Bucket nuevo se rechaza; no se crea tasa cero. Censura, antigüedad, mezcla y cambios de política siguen requiriendo validación.
