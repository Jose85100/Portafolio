# GARCH sobre la TRM oficial: evidencia de aplicación

## Problema y decisión

Una entidad con exposición cambiaria necesita estimar si la volatilidad de la TRM se agrupa en el tiempo y si un pronóstico condicional aporta información para dimensionar riesgo a un día. El laboratorio controlado del proyecto permite estudiar la dinámica GARCH cuando se conoce el proceso generador; esta edición evalúa qué sucede al aplicar GARCH(1,1)-t a una serie observada y reservar su último año para una comparación fuera de tiempo.

La evidencia procede del Banco de la República: 2.506 observaciones diarias de TRM entre 2020-01-01 y 2026-11-10. Al retener fechas de lunes a viernes, se usan 1.790 niveles y 1.789 retornos logarítmicos. Se estiman parámetros en 1.537 retornos iniciales y se pronostican los últimos 252, del 2025-11-24 al 2026-11-10.

## Método y resultados

Se ajusta una media constante con errores GARCH(1,1) y distribución t; los parámetros se mantienen fijos en el holdout, mientras la varianza condicional se actualiza con cada retorno realizado. La distribución t convierte volatilidad pronosticada en VaR al 99%.

| Evidencia | Resultado |
|---|---:|
| Convergencia del optimizador | Código 0 |
| Persistencia estimada `alpha + beta` | 0,9490 |
| Desviación estándar condicional media en holdout | 0,797% diario |
| VaR 99% medio en holdout | 2,075% diario |
| Excepciones / esperadas en 252 días | 3 / 2,52 |
| Kupiec UC p-valor | 0,768 |

El resultado no rechaza la cobertura incondicional al 99%, pero tres excepciones dan poca potencia para aceptar el modelo. El p-valor no demuestra calibración, independencia, estabilidad por régimen ni aptitud para límites.

## Flujo de análisis

```mermaid
flowchart LR
  A[SDMX BanRep<br/>TRM diaria] --> B[XML congelado<br/>+ SHA-256]
  B --> C[Validar fechas<br/>y valores positivos]
  C --> D[Filtrar lunes-viernes<br/>Δlog(TRM)]
  D --> E[GARCH(1,1)-t<br/>1.537 observaciones]
  E --> F[Pronóstico 252 días<br/>VaR 99%]
  F --> G[Conteo de excepciones<br/>+ Kupiec UC]
```

## Registro de decisiones y límites

| Decisión | Alternativa | Razón y coste |
|---|---|---|
| Usar retornos logarítmicos en días hábiles | Incluir todos los días del calendario | Evita contabilizar días de fin de semana como observaciones de mercado; conserva feriados cuando BanRep publica una fecha. |
| Estimar una vez y mantener parámetros fijos durante la prueba | Reestimar cada día | Separa parámetros de entrenamiento de resultados del holdout; no evalúa políticas de recalibración. |
| Reportar un modelo univariado y una prueba de cobertura | Afirmar aptitud para trading o hedge | La serie TRM no contiene costos, posiciones, hedge instrument ni precio ejecutable; no identifica rentabilidad ni efectividad de cobertura. |

La TRM es una tasa de referencia COP/USD y no un precio al que se garantice ejecutar una transacción. El backtest de 252 observaciones y pocas excepciones no tiene potencia suficiente para validar una cola extrema. Para uso institucional hacen falta retornos ejecutables, exposiciones, costos, reglas de recalibración, validación de independencia y pruebas de estrés aprobadas.

El [snapshot y la ficha de datos](../data/README.md), [runner](../official_application.py), [pronósticos](../data/official/garch_trm_forecasts.csv), [resumen](../data/official/application_summary.json) y [figura](figures/trm-garch-var99.png) permiten auditar y reproducir esta edición.
