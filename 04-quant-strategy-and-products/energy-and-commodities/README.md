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

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Proceso suave OU/Gaussiano sin restricciones físicas.** Base: Saltos de escasez, clima, congestión y generación renovable en dinámica spot. **Innovación a probar:** Comparar colas, picos y forecast por hora contra baseline fuera de muestra. **Prueba decisiva:** undefined
- **2. Despacho determinístico con valor terminal fijo.** Base: Flexibilidad de almacenamiento valorada como control estocástico con degradación y restricciones. **Innovación a probar:** Medir ahorro/valor de opción frente a política fija y verificar factibilidad física en trayectorias. **Prueba decisiva:** undefined
- **3. Curva de carry/roll yield con estacionalidad simple.** Base: Factores de estacionalidad y almacenamiento específicos por commodity/entrega. **Innovación a probar:** Probar precisión de curva y cobertura frente a carry simple en contratos reservados. **Prueba decisiva:** undefined
- **4. Cobertura de precio y FX por separado.** Base: Cobertura conjunta que incorpora riesgo de base y dependencia en margen local. **Innovación a probar:** Comparar varianza de margen y costo frente a coberturas separadas en shocks conjuntos. **Prueba decisiva:** undefined
- **5. Contrato baseload fijo como proxy de compra renovable.** Base: Contrato horario/pay-as-produced bajo canibalización y descalce de demanda. **Innovación a probar:** Comparar costo total, volumen descubierto y sensibilidad frente a baseload y mercado spot. **Prueba decisiva:** undefined
