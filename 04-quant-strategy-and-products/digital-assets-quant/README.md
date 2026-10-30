# Activos digitales y tokenización cuantitativa

Estudios de valoración, liquidez y diseño económico de activos digitales. El análisis no presupone que tokenizar cree valor por sí mismo: compara con una estructura financiera equivalente no tokenizada.

## Cinco ideas

1. **Modelo de liquidez para activos tokenizados**
   - Simular libro de órdenes, profundidad, concentración de tenedores y redenciones bajo distintos tamaños de emisión.
   - Aporte: estimar descuentos de salida y necesidades de creadores de mercado en mercados fragmentados.

2. **Diseño de reservas para tokens respaldados**
   - Optimizar mezcla de efectivo, instrumentos líquidos y vencimientos contra retiros estocásticos y costos de oportunidad.
   - Reportar cobertura por escenario, horizonte de liquidación y sensibilidad a haircut.

3. **Trazabilidad de flujos y riesgo de concentración**
   - Construir métricas de concentración de wallets, dependencia de puentes y exposición a entidades intermediarias con datos públicos de cadena.
   - Distinguir direcciones observadas de identidades verificadas y cuantificar incertidumbre de atribución.

4. **Tokenización de flujos de pago**
   - Evaluar derechos sobre ingresos futuros con waterfall, reservas, límites de anticipo y reglas de amortización.
   - Comparar costo de capital y riesgo de mora operativa con factoring o titularización tradicional.

5. **Mecanismo de redención y corrida**
   - Simular decisiones de tenedores bajo descuentos, congestión, retrasos y pérdida de confianza; probar colas y límites de redención.
   - Aporte: diseñar señales y reglas transparentes de liquidez sin prometer paridad incondicional.

## Controles

Documentar derechos legales subyacentes, custodia, oráculos, validadores, puentes, costos de red y escenarios de recuperación. Los indicadores on-chain son señales parciales, no prueba automática de solvencia o identidad.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Profundidad de libro observada como proxy de liquidez.** Base: Estimar capacidad de redención incorporando concentración, colas y mercados fragmentados. **Innovación a probar:** Contrastar descuento de salida y absorción de órdenes frente a profundidad simple bajo corridas simuladas. **Prueba decisiva:** undefined
- **2. Ratio estático de reservas sin calendario de liquidación.** Base: Reserva optimizada por vencimiento, haircut, correlación y retiros estocásticos. **Innovación a probar:** Probar cobertura por horizonte y costo de oportunidad contra ratio fijo, incluyendo ventas forzadas. **Prueba decisiva:** undefined
- **3. Heurística de etiquetar wallets como entidades.** Base: Grafo con incertidumbre de atribución y propagación explícita de confianza. **Innovación a probar:** Validar precisión con etiquetas verificadas y reportar sensibilidad de concentración a falsos enlaces. **Prueba decisiva:** undefined
- **4. Factoring/titularización tradicional con documentación fuera de cadena.** Base: Flujos con derechos, waterfall y conciliación on/off-chain instrumentados. **Innovación a probar:** Comparar costo/tiempo de conciliación y recuperación ante errores con proceso tradicional equivalente. **Prueba decisiva:** undefined
- **5. Promesa de redención a la par o pausa discrecional.** Base: Mecanismo de cola/regla de liquidez previamente especificado con escenarios de congestión. **Innovación a probar:** Evaluar ejecución contractual y contención de retiros sin asumir que el token conserva paridad. **Prueba decisiva:** undefined
