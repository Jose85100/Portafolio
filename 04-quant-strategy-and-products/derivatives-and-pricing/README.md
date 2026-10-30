# Derivados y valoración cuantitativa

Línea dedicada a valoración, calibración y cobertura de instrumentos financieros. Se documentan hipótesis de modelo, convenciones y error de aproximación; los resultados de riesgo agregados se remiten a 03-financial-risk.

## Cinco ideas

1. **Curvas de descuento multicurva**
   - Construir curvas OIS y de proyección desde instrumentos de mercado y comparar bootstrap con ajustes suaves monotónicos.
   - Medir error de repricing, sensibilidad a nodos y comportamiento con cotizaciones escasas.

2. **Superficie de volatilidad sin arbitraje**
   - Ajustar sonrisas y superficies en strikes y vencimientos imponiendo consistencia de precios, convexidad y restricciones de calendar spread.
   - Comparar SVI parametrizado con splines penalizados; reportar dónde los datos no identifican la superficie.

3. **Valoración de opciones con saltos y volatilidad estocástica**
   - Contrastar Black–Scholes, Heston y modelos con saltos en opciones europeas usando transformadas, árboles o Monte Carlo.
   - Aporte: mapa de error por moneyness y vencimiento, y prueba de estabilidad de calibración.

4. **Cobertura discreta con costos de transacción**
   - Evaluar delta hedging bajo rebalanceo discreto, spreads, gaps y restricciones de inventario.
   - Optimizar frecuencia de cobertura y cuantificar tracking error frente a cobertura continua idealizada.

5. **Valoración de derivados de energía y clima**
   - Diseñar contratos sobre precios de energía, precipitación o temperatura con procesos estacionales, reversión a la media y riesgo de base.
   - Entregable: simulador de escenarios, curva de pagos y análisis de sensibilidad; distinguir valoración física de valoración bajo medida de riesgo.

## Protocolo

Especificar numerario, medida, calendario, day count, colateral, fuentes de precios y tratamiento de datos. Comparar resultados con soluciones analíticas o benchmarks independientes cuando existan.
