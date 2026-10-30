# Diseño cuantitativo de productos financieros

Ideas para diseñar productos con pagos, tarifas e incentivos transparentes. Cada propuesta requiere evaluación de rentabilidad, conducta del cliente, operación y protección del consumidor.

## Cinco ideas

1. **Ahorro con rendimiento escalonado y metas**
   - Vincular tasa o beneficio a plazo, saldo y cumplimiento de metas, con opción de retiro parcial.
   - Modelar costo de fondeo, sensibilidad de permanencia y valor para distintos perfiles de uso.

2. **Crédito con cuota adaptativa a ingresos observables**
   - Permitir bandas de cuota que se ajusten a flujos de ingreso con reglas predefinidas, techo de plazo y amortización mínima.
   - Simular escenarios de volatilidad de ingresos, costo total y riesgo de extensión; comparar con cuota fija.

3. **Financiación de inventario con repago por ventas**
   - Diseñar anticipo cuyo repago siga ventas liquidadas, con límites de tasa efectiva, pausa por estacionalidad y liquidación clara.
   - Optimizar porcentaje de retención y tope de plazo bajo escenarios de flujo y caída de ventas.

4. **Producto de cobertura de precio para comercios**
   - Ofrecer protección simple frente a FX, insumos o tasas mediante contratos o tarifas preacordadas.
   - Comparar cobertura lineal, collar y precio fijo, mostrando costo, escenarios de pago y riesgo de contraparte.

5. **Cuenta transaccional con reserva automática**
   - Separar liquidez operativa y ahorro mediante reglas adaptativas de barrido que respeten pagos próximos y colchón mínimo.
   - Medir beneficio neto, frecuencia de reversión y riesgo de sobregiro frente a una regla fija.

## Evaluación

Publicar fórmula de pago y tarifas, ejemplos numéricos, costos, escenarios adversos, sensibilidad a comportamiento y condiciones de salida. No confundir innovación de producto con recomendación comercial.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Tasa escalonada definida solo por saldo/plazo.** Base: Regla por metas que incorpora permanencia, costo de fondeo y necesidad de liquidez. **Innovación a probar:** Experimento o simulación de comportamiento debe mejorar ahorro neto/retención sin elevar retiros dañinos. **Prueba decisiva:** undefined
- **2. Cuota fija o periodo de gracia estándar.** Base: Cuota ligada a ingresos con amortización mínima y límites explícitos de extensión. **Innovación a probar:** Comparar costo total, mora y plazo frente a cuota fija en trayectorias de ingresos diversas. **Prueba decisiva:** undefined
- **3. Retención fija sobre ventas o anticipo convencional.** Base: Repago variable con tope de costo total y tratamiento estacional de ingresos. **Innovación a probar:** Probar menor déficit de caja del comercio sin aumentar costo efectivo ni dependencia de ventas futuras. **Prueba decisiva:** undefined
- **4. Cobertura genérica de tasa/FX con prima uniforme.** Base: Cobertura modular ajustada a flujo y tolerancia de caja del comercio. **Innovación a probar:** Comparar costo, riesgo residual y comprensibilidad con producto estándar bajo shocks y riesgo de base. **Prueba decisiva:** undefined
- **5. Barrido fijo de excedentes o ahorro manual.** Base: Reserva automática que pronostica pagos próximos y mantiene colchón mínimo. **Innovación a probar:** Medir rendimiento adicional sin aumentar sobregiros, rechazos ni falta de liquidez frente a regla fija. **Prueba decisiva:** undefined
