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

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Bootstrap estándar con una curva de descuento/proyección.** Base: Curvas multicurva con restricciones de consistencia y penalización de inestabilidad. **Innovación a probar:** Comparar repricing y sensibilidad a cotizaciones faltantes frente a bootstrap convencional. **Prueba decisiva:** undefined
- **2. Ajuste de smile sin restricciones globales.** Base: Superficie con restricciones de no arbitraje incorporadas durante calibración. **Innovación a probar:** Evaluar error de precio y contar violaciones de butterfly/calendar antes y después en cotizaciones reservadas. **Prueba decisiva:** undefined
- **3. Black–Scholes o Heston como benchmarks.** Base: Saltos más volatilidad estocástica calibrados por vencimiento y moneyness. **Innovación a probar:** Validar error fuera de muestra y estabilidad de parámetros frente a benchmarks más simples. **Prueba decisiva:** undefined
- **4. Delta hedge continuo y sin fricción.** Base: Política discreta que optimiza costo de transacción, riesgo de tracking e inventario. **Innovación a probar:** Trazar frontera costo-error y validar que domina políticas fijas en escenarios de volatilidad y gap. **Prueba decisiva:** undefined
- **5. Curva de commodity estándar sin factor físico explícito.** Base: Valoración de energía/clima con estacionalidad, reversión, riesgo de base y variable física. **Innovación a probar:** Comparar error de hedge y calibración con benchmark financiero sin factor físico. **Prueba decisiva:** undefined
