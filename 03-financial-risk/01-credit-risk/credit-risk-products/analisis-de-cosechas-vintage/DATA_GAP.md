# Brecha de datos: cosechas de crédito

**Estado:** laboratorio controlado; no hay una companion observada con grano compatible. La búsqueda de evidencia pública no encontró un panel que permita estimar curvas de incumplimiento por cohorte de originación. No se derivan PD, vintage curves ni validación MRM de saldos agregados.

## Pregunta que requiere datos

El método compara la incidencia acumulada de primer default por mes desde originación. Su unidad mínima es **crédito seudonimizado × mes de observación**, con fecha de originación, estado del crédito y primera fecha de default. Se deben comparar cosechas con ventana de desempeño y población elegible consistentes, y tratar cierres, prepago, cura, castigo y censura.

## Fuentes públicas revisadas

| Fuente | Grano y campos relevantes | Por qué no identifica cosechas | Uso que sí permite |
|---|---|---|---|
| [SFC, distribución de cartera por producto (`rvii-eis8`)](https://www.datos.gov.co/en/en/Public-Finance/Distribuci-n-de-cartera-por-producto/rvii-eis8) | Entidad reportante × corte mensual × producto/modalidad × renglón; saldos brutos, categorías de mora y calificación. | No publica llave persistente de crédito ni deudor, fecha de originación, flujo de entrada/salida o primera transición a default. La companion [`observed-sfc-product-risk-mix`](../perdida-esperada-pd-lgd-ead/observed-sfc-product-risk-mix/) usa proporciones de saldo D/E y está limitada a monitoreo agregado por producto; no se vuelve un vintage al reordenar meses. | Mezcla agregada de saldos por producto y corte, con advertencia de composición. |
| [ICETEX, comportamiento de cartera (`dugh-vkir`)](https://www.datos.gov.co/en/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir) | Corte × departamento × etapa del crédito; conteos por estado de mora y saldos agregados. | No contiene IDs de operación, fecha de originación ni trayectorias que conecten una cuenta entre cortes. Su universo es crédito educativo ICETEX, no una muestra de originaciones bancarias. | Prevalencia agregada de mora por departamento/etapa, con las limitaciones documentadas en el companion observado ICETEX. |
| [UCI Default of Credit Card Clients, dataset 350](https://archive.ics.uci.edu/dataset/350/default%2Bof+credit+card+clients) | Clientes taiwaneses, atributos y estados de pago de abril–septiembre de 2005, etiqueta binaria de default del siguiente mes; 30.000 observaciones. | Es un corte individual extranjero con historial retrospectivo de pagos, no un panel cuenta–mes con originación, exposición por corte y primera transición a default. El raw canónico no está disponible en este entorno y no se calcula benchmark aquí. | Si se recupera el archivo oficial, evaluación académica extranjera del scorecard en su horizonte de un mes, no validación colombiana ni cosechas. |

## Brecha exacta para desbloquear una aplicación observada

El dueño de cartera o un custodio autorizado tendría que suministrar snapshots históricos versionados con:

1. `account_id` seudonimizado y persistente; producto, moneda y población elegible.
2. Fecha de originación, fecha de observación y fecha de extracción/publicación (as-known-at).
3. Saldo/exposición y días de mora por corte, más reglas versionadas de default, cura, prepago, castigo y cierre.
4. Fecha del primer evento de default y denominador de créditos observables; reglas explícitas de censura y entradas tardías.
5. Cohortes con horizonte comparable, por lo menos 12 meses de seguimiento para una curva a 12 meses, más período fuera de desarrollo para validación temporal independiente.
6. Reconciliación de conteos y saldos contra el sistema fuente, diccionario, linaje, hash por vintage y aprobación de uso de los datos.

Sin estos campos no se puede calcular `defaults_h / cuentas_originadas_vintage`, incidencia acumulada, hazard observada ni comparar cosechas. No es válido crear esos campos a partir de conteos de mora agregados ni tratar categorías de calificación/mora como estados de una misma cuenta.

## Decisión y límite

Se conserva el laboratorio como demostración matemática controlada. Las fuentes públicas anteriores permiten contexto de stocks, pero no validan el método de cosechas. No se adjunta una curva observada ni se reporta desempeño. Cuando exista el panel institucional descrito, la primera entrega deberá ser conciliación/calidad y curvas descriptivas con censura explícita; cualquier inferencia de PD requiere definición de target, ventanas temporales y validación independiente aprobadas antes de modelar.
