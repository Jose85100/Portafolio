# Cobertura de aplicaciones: valoración y contraparte

Los notebooks de [wrong-way y CVA](wrong-way-risk-xva/), [validación de VaR](model-validation/) y [bandas bid–ask](pricing-uncertainty-bounds/) son ejercicios acotados. El de opciones depende de una captura diferida que puede no estar disponible; ninguno valida valoración, cobertura o riesgo de contraparte de una entidad.

| Tema sin aplicación específica | Datos mínimos para una aplicación pertinente |
|---|---|
| [CVA/DVA/FVA](xva/) | Transacciones y valoraciones por contraparte, neteo, acuerdos de colateral, curvas de crédito y financiación. El ejercicio de CVA relacionado no estima DVA ni FVA. |
| [Liquidación](settlement-risk/) | Pagos e instrucciones fechadas, confirmaciones, retrasos, fallos y exposiciones durante el ciclo de liquidación. |
| [Margen y colateral](collateral-margin-dynamics/) | Contratos y acuerdos de margen, valoraciones, llamadas, garantías y tiempos de cumplimiento. |
| [Red intradía de pagos](intraday-payment-network/) | Pagos entre participantes con fecha y hora, saldos intradía y reglas de procesamiento, anonimizados. |

Una serie agregada o una hipótesis sin observaciones relevantes puede servir para un escenario ilustrativo; no cierra estas brechas de aplicación ni valida el modelo de cada tema.
