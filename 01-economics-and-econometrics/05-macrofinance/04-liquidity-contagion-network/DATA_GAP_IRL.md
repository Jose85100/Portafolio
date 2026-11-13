# Brecha de datos para contagio de liquidez

## Pregunta y evidencia disponible

El laboratorio modela faltantes de caja y cascadas entre entidades. La fuente oficial revisada es el Indicador de Riesgo de Liquidez (IRL) de la SFC, disponible en el [companion observado](../../../03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/README.md). La SFC define `IRL = 100 × ALM_promedio_mensual / RLN_promedio_mensual_30d` y publica un mínimo prudencial de 100%.

El XLS histórico tiene grano entidad reportante × corte mensual y cubre marzo de 2020–diciembre de 2022: 34 cortes, 1.438 razones válidas y 40–44 entidades por corte. Hay tres filas con IRL faltante omitidas, ninguna llave entidad-mes duplicada y 1.438/1.438 razones concilian con ALM/RLN dentro de tolerancia 0,00051. Su SHA-256 es `52b24483f73b7a7402b26708826b417d5169ec2604c2aaacb5007a5ba72296e0`.

La vintage posterior del boletín SFC de agosto de 2026 aporta 12 observaciones de componentes reconstruidas por tipo × fecha para agosto de 2025, julio de 2026 y agosto de 2026. Son cortes discontinuos, no una serie mensual ni panel entidad-mes. El PDF tiene SHA-256 `e38b879140f70d523b655af2aa72c12531f802473604d99bddc15fc57f8b985d`; la fuente advierte que las cifras CUIF están sujetas a revisión y fueron reportadas hasta el 25 de septiembre de 2026.

En diciembre de 2022, corte final del XLS, la mediana por entidad fue 213,1%, el mínimo 112,8% y ninguna de las 44 entidades observadas estuvo por debajo de 100%. Estos datos describen cobertura prudencial reportada. El companion ya documenta esa distribución; este proyecto no replica esas métricas.

## Por qué el IRL no identifica contagio ni primera ruptura

Un ratio mensual de cobertura de 30 días no muestra qué entidad presta a otra, qué pagos vencen en cada fecha, la secuencia intramensual de flujos, ni la caja utilizable después de haircuts y encumbrance. Tampoco informa si una trayectoria tuvo un faltante de efectivo. En consecuencia, el IRL puede servir como referencia marginal para revisar plausibilidad de buffers agregados frente a un umbral; no estima la matriz `W`, el shock de liquidez, la propagación ni el tiempo hasta caja negativa.

**El IRL no valida ni calibra el modelo de primera ruptura.** Superar el 100% no prueba que una entidad no haya tenido un faltante intradía, y cruzar 100% no equivale por sí solo a una ruptura de caja o contagio. No se debe etiquetar ninguna observación mensual como evento de falla sin un resultado de caja observado y una definición operacional de evento.

El mismo límite afecta a proyectos macrofinancieros cercanos: el IRL no resuelve descalces por moneda para `FX Liquidity Mismatch`, exposiciones bilaterales para el nexo soberano-bancario ni flujo de transacciones por ventana para riesgo sistémico de pagos.

## Granularidad mínima requerida

| Componente | Grano requerido | Uso |
|---|---|---|
| Entradas, salidas y saldo líquido | entidad estable × fecha (ideal diario o intradía) × moneda × banda de vencimiento | reconstruir caja disponible y primera ruptura bajo estrés |
| Obligaciones entre contrapartes | entidad origen × entidad destino × fecha/vencimiento × moneda × monto | construir matriz bilateral de contagio y cascadas |
| Activos y colateral | entidad × activo × fecha × moneda, con haircut, encumbrance y capacidad/plazo de monetización | estimar buffers realmente utilizables y ventas forzadas |
| Pagos y liquidación | participante × obligación contraparte × ventana/fecha de liquidación × moneda × estado (liquidado/fallido) | medir cascadas de pagos e intradía |
| Evento observado | entidad × fecha/hora, déficit de caja o incumplimiento definido, severidad y resolución | validar primera ruptura, duración y falsos negativos |
| Vintage y entidad | identificador estable pseudonimizado × fecha de observación y de publicación/revisión | backtest as-known-at sin fuga temporal |

Se requiere historia que incluya periodos de tensión y variación suficiente en resultados de liquidez. Las fuentes públicas revisadas no contienen este detalle transaccional o de tesorería. La siguiente aplicación cuantitativa legítima sería contrastar el modelo con trayectorias de caja observadas bajo gobernanza de datos supervisora o interna; hasta entonces la simulación permanece sintética y el IRL solo contextualiza el buffer regulatorio.
