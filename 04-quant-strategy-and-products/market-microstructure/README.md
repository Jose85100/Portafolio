# Microestructura y ejecución de órdenes

Estudios sobre cómo las órdenes se convierten en transacciones reales. El foco es ejecución, costos y calidad de mercado; la generación de señales de inversión queda en quantitative-trading.

## Cinco ideas

1. **Modelo de impacto de mercado por tamaño**
   - Estimar costo de ejecución frente a participación del volumen, volatilidad y profundidad.
   - Comparar impacto lineal y modelos de raíz cuadrada con validación por activo y periodo.

2. **Ejecución óptima con urgencia y riesgo de precio**
   - Distribuir una orden entre tiempo y participación minimizando costo esperado más penalización por riesgo de no ejecución.
   - Contrastar soluciones Almgren–Chriss con políticas adaptativas sujetas a límites.

3. **Selección adversa y toxicidad del flujo**
   - Medir si las transacciones ejecutadas preceden movimientos desfavorables, condicionando por spread, tamaño y hora.
   - Aporte: separar costo de spread, impacto transitorio y permanente.

4. **Enrutamiento entre venues**
   - Asignar órdenes entre bolsas, internalizadores o proveedores según precio, latencia, probabilidad de fill y tarifas.
   - Simular fallas, datos retrasados y cambios de profundidad; registrar por qué se eligió cada ruta.

5. **Calidad de ejecución para pagos y FX**
   - Comparar precio de referencia con precio ejecutado, demora, rechazos y slippage por contraparte y franja horaria.
   - Crear un benchmark auditable de mejor ejecución con bandas de incertidumbre y análisis de colas.

## Datos y cautelas

Usar snapshots con timestamp y reglas de limpieza reproducibles. Los datos agregados o retrasados limitan inferencias sobre prioridad de cola y latencia. No afirmar rentabilidad potencial sin costos completos.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Impacto lineal o raíz cuadrada universal.** Base: Impacto condicionado por profundidad, volatilidad, activo y participación en volumen. **Innovación a probar:** Comparar error de costo ejecutado fuera de muestra contra benchmark universal por activo y régimen. **Prueba decisiva:** undefined
- **2. TWAP/VWAP fijo como regla de ejecución.** Base: Control de urgencia que equilibra impacto, riesgo de precio e incompletitud. **Innovación a probar:** Trazar costo total versus fill rate frente a TWAP/VWAP en simulación y datos de ejecución reservados. **Prueba decisiva:** undefined
- **3. Order flow firmado como único proxy de toxicidad.** Base: Separar spread, impacto permanente y markout condicional al estado de mercado. **Innovación a probar:** Demostrar calibración de markout y señal incremental sobre spread/proxy simple. **Prueba decisiva:** undefined
- **4. Mejor precio visible como regla de ruteo.** Base: Ruteo que optimiza precio ejecutable, fill, latencia, tarifas y confiabilidad. **Innovación a probar:** Comparar ahorro neto y tasa de ejecución ante fallas y datos retrasados con best-price routing. **Prueba decisiva:** undefined
- **5. Arrival price con una sola referencia.** Base: Benchmark de calidad de ejecución ajustado por tamaño, latencia, moneda y liquidez. **Innovación a probar:** Validar comparabilidad entre venues/proveedores y sensibilidad a benchmark alternativo. **Prueba decisiva:** undefined
