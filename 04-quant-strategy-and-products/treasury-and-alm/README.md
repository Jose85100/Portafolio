# Tesorería y gestión de activos y pasivos (ALM)

Esta línea optimiza decisiones de balance, fondeo y liquidez económica. No replica los modelos regulatorios de riesgo de 03-financial-risk: estudia composición, costos, plazos y decisiones bajo escenarios.

## Cinco ideas

1. **Calce de activos y pasivos por flujo**
   - Optimizar cartera de activos para cubrir pagos futuros por moneda y banda temporal, con límites de duración, liquidez y concentración.
   - Comparar inmunización clásica con programación por escenarios y costos de transacción.

2. **Transfer pricing de fondos por plazo y opcionalidad**
   - Diseñar tasas internas de transferencia que distribuyan costo de fondeo, liquidez y opciones de prepago entre productos y unidades.
   - Aporte: comparar reglas planas con curvas marginales por moneda, plazo y comportamiento.

3. **Optimización de mezcla de fondeo**
   - Elegir depósitos, deuda mayorista, titularización y capital según costo total, estabilidad, plazo y capacidad disponible.
   - Núcleo: optimización multi-periodo con restricciones de concentración y escenarios de renovación.

4. **Riesgo de prepago y retiro conductual para ALM**
   - Estimar distribuciones de prepago de créditos y retiros de depósitos a partir de tasas, antigüedad y comportamiento agregado.
   - Traducir modelos conductuales a flujos y sensibilidad de margen, sin tratar predicciones como certezas.

5. **Gestión conjunta de liquidez intradía y costo**
   - Programar reservas y pagos en sistemas de liquidación con ventanas, colas, penalidades y líneas contingentes.
   - Métrica: costo esperado de liquidez más retrasos; comparar heurísticas operativas con programación lineal entera.

## Entregables

Curvas y escenarios con unidades explícitas, libro de supuestos, comparación de políticas de balance y pruebas de sensibilidad. Diferenciar análisis económico de cumplimiento prudencial.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Gap de duración o cobertura agregada por banda.** Base: Optimización de flujos multi-periodo por moneda, liquidez y costo. **Innovación a probar:** Comparar faltantes de caja y valor económico frente a duration matching bajo shocks comunes. **Prueba decisiva:** undefined
- **2. FTP plano por producto/plazo.** Base: Precio marginal de fondos que incorpora plazo, opcionalidad y costo de liquidez. **Innovación a probar:** Validar atribución consistente de margen y cambios de incentivos frente a FTP plano. **Prueba decisiva:** undefined
- **3. Selección por costo unitario más bajo.** Base: Mezcla multi-fuente con concentración, renovaciones, capacidad y escenarios de mercado. **Innovación a probar:** Medir costo total y brechas de refinanciación frente a mezcla mínima y estrategia vigente. **Prueba decisiva:** undefined
- **4. Curvas históricas de prepago/retiro agregadas.** Base: Modelos conductuales condicionados a tasas, antigüedad y fricciones con incertidumbre explícita. **Innovación a probar:** Comparar pronóstico de flujos por cohorte y estabilidad de valor del balance fuera de muestra. **Prueba decisiva:** undefined
- **5. Buffer fijo y regla FIFO intradía.** Base: Optimización de pagos, neteo y fondeo con ventanas y penalidades de demora. **Innovación a probar:** Comparar costo y puntualidad frente a buffer/FIFO, verificando factibilidad de liquidación. **Prueba decisiva:** undefined
