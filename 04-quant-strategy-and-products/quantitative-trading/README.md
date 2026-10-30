# Quantitative trading

Área para investigar reglas y sistemas de decisión de inversión en mercados. El objetivo es distinguir señal estadística de rentabilidad ejecutable después de costos, restricciones y riesgo de selección.

## Cinco ideas

1. **Estrategias cross-sectional con señales alternativas**
   - Combinar momentum, calidad, carry y revisiones de expectativas con regularización y ventanas temporales anidadas.
   - Evaluación: rendimiento neto, turnover, capacidad y estabilidad por régimen; universo punto-en-el-tiempo para evitar sesgo de supervivencia.

2. **Estrategia de reversión a la media con inventario**
   - Estimar bandas adaptativas y tamaño de posición condicionado por volatilidad, liquidez y costo de salida.
   - Aporte: límites explícitos de inventario y prueba de quiebres de cointegración; no asumir reversión permanente.

3. **Asignación dinámica entre señales**
   - Combinar estrategias mediante modelo de estado/regímenes y actualización bayesiana, con presupuesto de riesgo común y límites de rotación.
   - Comparar contra pesos iguales y selección por Sharpe histórico; validar con walk-forward y periodos de estrés.

4. **Trading de eventos con incertidumbre de calendario**
   - Estudiar anuncios programados y sorpresas económicas como eventos; modelar distribución de retornos, gaps y liquidez antes/después.
   - Aporte: reglas de abstención cuando el spread o la incertidumbre superan el beneficio esperado.

5. **Estrategia de cobertura dinámica para exposición FX**
   - Optimizar proporción y frecuencia de cobertura de flujos internacionales incorporando forwards, carry, spreads y error de pronóstico.
   - Métrica: costo total de cobertura y distribución de desviación presupuestal frente a no cubrir y a cobertura fija.

## Requisitos mínimos

Backtest sin look-ahead, datos versionados, costos y slippage parametrizados, benchmark ingenuo, validación fuera de muestra y análisis de sensibilidad. Toda estrategia se trata como hipótesis hasta replicarse con datos independientes.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Señales aisladas y portafolio equal-weight.** Base: Ensamble cross-sectional regularizado con señales alternativas disponibles punto-en-tiempo. **Innovación a probar:** Ablation y walk-forward deben demostrar retorno neto incremental frente a equal-weight y señal individual. **Prueba decisiva:** undefined
- **2. Bandas fijas de reversión y tamaño estático.** Base: Umbrales que responden a inventario, volatilidad, liquidez y costo de salida. **Innovación a probar:** Comparar retorno neto, inventario extremo y drawdown frente a bandas fijas y benchmark buy-and-hold. **Prueba decisiva:** undefined
- **3. Pesos fijos o selección por Sharpe histórico.** Base: Ensamble con actualización bayesiana por régimen y presupuesto de riesgo compartido. **Innovación a probar:** Probar mejora neta fuera de muestra y descartar ganancia si depende de un único periodo/régimen. **Prueba decisiva:** undefined
- **4. Estudio de evento descriptivo sin costo de ejecución.** Base: Regla de entrada/salida condicionada por sorpresa, hora y liquidez observable. **Innovación a probar:** Exigir poder predictivo incremental y PnL neto tras spread/slippage en eventos no usados en diseño. **Prueba decisiva:** undefined
- **5. Ratio de cobertura fijo o mínima varianza incondicional.** Base: Cobertura condicional a flujo, carry, base y costo de rebalanceo. **Innovación a probar:** Demostrar menor error presupuestal neto de costos frente a no cubrir y hedge ratio fijo. **Prueba decisiva:** undefined
