# Inmobiliario e hipotecas cuantitativas

Análisis de valoración, financiación y flujos de bienes inmuebles y créditos hipotecarios. El foco es la decisión económica del activo y del contrato; los modelos de riesgo de crédito regulatorio quedan en `03-financial-risk`.

## Cinco ideas

1. **Valoración probabilística de inmuebles con comparables**
   - Estimar distribución de valor usando características, ubicación, comparables y fecha de transacción, con ajuste por liquidez y calidad de dato.
   - Comparar modelos hedónicos, cuantiles y enfoques espaciales; reportar intervalos, no solo una cifra puntual.

2. **Prepago hipotecario y opciones del prestatario**
   - Modelar refinanciación, amortización anticipada y permanencia según tasas, antigüedad, saldo y fricciones.
   - Valorar el efecto de la opción de prepago sobre duración y flujo; probar estabilidad en ciclos de tasas distintos.

3. **Economía de renta y vacancia**
   - Proyectar ingreso neto considerando renta, vacancia, gastos, mantenimiento y renovaciones contractuales.
   - Calcular valor presente y cobertura de deuda bajo escenarios de ocupación y costos, con sensibilidad a ubicación y tipo de inmueble.

4. **Precio de vivienda y accesibilidad**
   - Estimar brechas entre precios, ingresos, arriendos y costo de financiación por segmento y ciudad.
   - Construir escenarios de asequibilidad y cuotas; separar correlación local de efectos causales de política o infraestructura.

5. **Valoración de activos inmobiliarios tokenizados**
   - Conectar tasación, flujos de renta, costos, derechos económicos y liquidez secundaria.
   - Cuantificar descuento por iliquidez, concentración de tenedores y riesgo de descalce entre promesas de salida y venta del activo.

## Datos y límites

Documentar georreferenciación, privacidad, fechas de avalúo, sesgo de selección y diferencias entre precio anunciado y transado. No presentar estimaciones automatizadas como avalúos oficiales.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. AVM de punto único hedónico.** Base: Valor probabilístico espacial con cuantiles, fecha y liquidez explícitos. **Innovación a probar:** Validar cobertura de intervalos y error por zona/tipo contra regresión hedónica. **Prueba decisiva:** undefined
- **2. Tasa de prepago histórica agregada.** Base: Opción de refinanciación condicionada a incentivos, fricciones y tasas. **Innovación a probar:** Comparar error de cashflow/prepago y valor de opción frente a CPR histórica. **Prueba decisiva:** undefined
- **3. Cap rate estático sobre renta estabilizada.** Base: Flujos netos probabilísticos con vacancia, mantenimiento y renovación. **Innovación a probar:** Validar error de NOI y sensibilidad de VPN frente a capitalización estática. **Prueba decisiva:** undefined
- **4. Ratio precio-ingreso como indicador único.** Base: Accesibilidad por cuota, arriendo, ingreso y escenarios de crédito. **Innovación a probar:** Probar poder descriptivo por segmento y documentar límites causales del indicador. **Prueba decisiva:** undefined
- **5. Yield del inmueble como valoración tokenizada.** Base: Descuento por derechos, iliquidez y concentración frente al activo no tokenizado. **Innovación a probar:** Comparar escenarios de salida y waterfall con valuación tradicional; explicitar supuestos legales. **Prueba decisiva:** undefined
