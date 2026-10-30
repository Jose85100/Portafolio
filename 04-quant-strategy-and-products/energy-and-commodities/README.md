# Energía y materias primas

Modelos cuantitativos para valoración, cobertura y decisiones en mercados de electricidad, combustibles y productos agrícolas. La carpeta combina series de precios, restricciones físicas y contratos financieros.

## Cinco ideas

1. **Precio spot eléctrico con restricciones físicas**
   - Modelar no almacenamiento, congestión, generación renovable, demanda y saltos de escasez.
   - Comparar modelos de reversión a la media, procesos de salto y modelos de factores; medir error en precios y colas por hora.

2. **Valoración de almacenamiento y flexibilidad**
   - Valorar baterías o embalses como opciones de comprar, almacenar y vender energía sujeto a capacidad, eficiencia y degradación.
   - Formular control estocástico o programación dinámica; comparar política óptima con despacho por reglas fijas.

3. **Curvas forward de commodities estacionales**
   - Estimar curvas de futuros incorporando almacenamiento, costo de acarreo, estacionalidad y restricciones de entrega.
   - Analizar pendiente, roll yield y errores de cobertura de productores y consumidores.

4. **Cobertura conjunta de precio, base y tipo de cambio**
   - Diseñar cobertura para un productor que vende en moneda local pero recibe precio de referencia global.
   - Optimizar varianza o expected shortfall de margen operativo con futuros, forwards y contratos físicos; reportar riesgo de base residual.

5. **Contratos de compra de energía renovable**
   - Comparar contratos pay-as-produced, baseload y collar frente a perfiles horarios de demanda y generación.
   - Simular costo total, volumen descubierto y sensibilidad a canibalización de precios y errores de pronóstico.

## Protocolo

Separar precio financiero de restricciones físicas y disponibilidad de activos. Registrar zona, unidad, resolución horaria, reglas de liquidación, límites de transmisión y escenarios de clima.
