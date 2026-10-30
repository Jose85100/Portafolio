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
