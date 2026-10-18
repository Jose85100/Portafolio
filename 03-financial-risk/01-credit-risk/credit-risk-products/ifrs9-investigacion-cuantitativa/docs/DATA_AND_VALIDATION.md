# Datos, temporalidad y validación

## Diccionario mínimo

| Tabla | Grano | Columnas críticas | Uso |
|---|---|---|---|
| Cohorte PD | Un contrato al origen | loan_id, score, segment, macro, origination_month, default_12m | Logit 12m y OOT |
| Panel PD | Contrato-mes aún en riesgo | loan_id, month, age_months, default, features conocidas | Supervivencia, sin filas después de default |
| Transiciones | Contrato-intervalo mensual | from_state, to_state, originación | Markov; estado 3 absorbente |
| Workouts completos | Un caso cerrado | collateral_ratio, segment, macro, loss_fraction, completion_month | LGD, con target descontado a default |
| Ventanas CCF | Una ventana cerrada hacia default | utilization, segment, macro, ccf, completion_month | Ajuste de CCF, no recuperación |
| Cartera al corte | Un contrato | product, balance, limit, coupon, eir, term_months, score, segment, rating, age_months | Predicción ECL |
| Política SICR | Un contrato | origin/current_lifetime_pd, dpd, watchlist, credit_impaired | Stage explícito, horizonte comparable |
| Recuperaciones S3 | Contrato-fecha | flujos netos y fechas desde reporte | Ruta de activos deteriorados |
| Matriz simplificada | Bucket-cohorte cerrada | exposure, discounted_shortfall | Universo distinto del factorial de préstamos |

Tasas y probabilidades en fracciones. Coupon y EIR anuales efectivas; PD/default en pasos mensuales; tiempos de recuperación en años. Todas las exposiciones deben estar en una moneda consistente. Los montos de muestra no son COP ni USD: son unidades arbitrarias.

## Generador y partición

La semilla de referencia es 20261018. En `synthetic_history`, 2.200 contratos tienen score continuo, segmento binario y macro constante por contrato. El hazard verdadero depende de esos atributos y edad; default detiene filas. El logit sólo recibe etiquetas maduras de 12m. El modelo de supervivencia recibe ventanas hasta 36m o default.

El rating evoluciona en un proceso Markov independiente del default verdadero condicional en score. Esto induce mala especificación y hace visible la diferencia entre una PD de rating y una calibración compatible con eventos observados. No presentar su comparación como benchmark neutral entre algoritmos.

Para construir un calendario sin ventanas de resultado superpuestas, las originaciones de entrenamiento van de 0 a 29 y su performance llega a 65; las originaciones OOT se desplazan a 66–83. No se entrena con OOT, pero esta separación temporal es **construida** y estacionaria: no reproduce crisis ni drift. Workouts y ventanas CCF son conjuntos independientes con su propia partición por fecha de cierre <30 / ≥30. No se ajustan hiperparámetros con OOT.

La cartera al corte tiene semilla independiente 61, dos segmentos, dos productos y vida remanente hasta 36m. El factorial usa la misma cartera en todas las configuraciones. La política SICR usa entradas sintéticas comparables, no una estimación histórica reconstruida.

## Métricas y qué no demuestran

- **PD:** AUC, Brier, log-loss, media predicha/observada y calibración agrupada para evento 12m. No sustituye backtest lifetime.
- **LGD:** MAE/RMSE/sesgo en casos completos posteriores. No corrige sesgo por cierre ni estima flujos abiertos.
- **CCF:** errores en fracción de cupo disponible; no equivale a error monetario de EAD.
- **ECL:** reconciliación mensual → escenario → contrato → agregado; sensibilidad a modelos, escenario y staging. No existe una ECL realizada observable sin definir sus componentes y horizonte; el factorial no valida exactitud contable global.
- **Bootstrap:** percentil 95%, 500 remuestras pareadas por contrato. Fija modelos, política y escenarios: mide variabilidad de mezcla de cartera en el contraste; no incertidumbre total de ECL.

`results/multimodel` contiene CSV de 18 configuraciones, métricas OOT, métricas reservadas LGD/CCF, bootstrap, parámetros y manifest. La CLI los regenera desde código. No se presenta un benchmark externo ni promesa de mejora de provisiones.

## Identidades independientes

1. q_m = h_m∏_{j<m}(1−h_j); suma(q)+S_H=1.
2. Markov de dos estados con default mensual .1 produce PD_H=1−.9^H.
3. Logit plano reproduce p12 al sumar 12 masas y 1−(1−p12)^3 a 36m.
4. Crédito a tasa cero de 120 a tres meses: EAD inicial mensual [120,80,40], luego cero.
5. Prepago independiente: EAD_CPR/EAD_contractual=(1−CPR)^((m−1)/12).
6. Recuperación de .6 del saldo a dos años, EIR .1: LGD=1−.6/1.1².
7. Stage 1 selecciona meses de default hasta 12; no selecciona meses de recuperación.
8. Stage 3 es independiente de la PD futura, LGD challenger y CCF de futuros desembolsos.
9. Matriz simplificada agrega pérdidas/saldos, no medias simples de tasas.

## Integración con datos reales

1. Congelar snapshot as-of con disponibilidad de features, vintage macro y estado de cada contrato.
2. Construir labels de default, observación/censura y recuperación con definiciones aprobadas; no mezclar cierre contable con cierre de gestión.
3. Construir ventanas de utilización conocidas al corte y EAD realizada sólo como etiqueta.
4. Separar entrenamiento, calibración, validación temporal y segmentos; no reutilizar este generador como pipeline productivo.
5. Calibrar escenarios con fuentes públicas trazables y relevancia económica de la cartera; preservar dependencia PD/LGD/EAD.
6. Reconciliar saldos, tasas y shortfalls con contabilidad y política. La provisión SFC se mantiene en una ruta separada.
7. Aprobar versiones, monitorear y definir reversión. El SQL entregado es un diseño de persistencia con smoke test, no un adaptador ETL.
