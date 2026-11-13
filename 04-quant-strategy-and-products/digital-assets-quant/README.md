# Activos digitales y tokenización cuantitativa

Estudios de valoración, liquidez y diseño económico de activos digitales. El análisis no presupone que tokenizar cree valor por sí mismo: compara con una estructura financiera equivalente no tokenizada.

## Cinco ideas

1. **[Modelo de liquidez para activos tokenizados](01-modelo-de-liquidez-para-activos-tokenizados/README.md)**
   - Simular libro de órdenes, profundidad, concentración de tenedores y redenciones bajo distintos tamaños de emisión.
   - Aporte: estimar descuentos de salida y necesidades de creadores de mercado en mercados fragmentados.

2. **[Diseño de reservas para tokens respaldados](02-diseno-de-reservas-para-tokens-respaldados/README.md)**
   - Optimizar mezcla de efectivo, instrumentos líquidos y vencimientos contra retiros estocásticos y costos de oportunidad.
   - Reportar cobertura por escenario, horizonte de liquidación y sensibilidad a haircut.

3. **[Trazabilidad de flujos y riesgo de concentración](03-trazabilidad-de-flujos-y-riesgo-de-concentracion/README.md)**
   - Construir métricas de concentración de wallets, dependencia de puentes y exposición a entidades intermediarias con datos públicos de cadena.
   - Distinguir direcciones observadas de identidades verificadas y cuantificar incertidumbre de atribución.

4. **[Tokenización de flujos de pago](04-tokenizacion-de-flujos-de-pago/README.md)**
   - Evaluar derechos sobre ingresos futuros con waterfall, reservas, límites de anticipo y reglas de amortización.
   - Comparar costo de capital y riesgo de mora operativa con factoring o titularización tradicional.

5. **[Mecanismo de redención y corrida](05-mecanismo-de-redencion-y-corrida/README.md)**
   - Simular decisiones de tenedores bajo descuentos, congestión, retrasos y pérdida de confianza; probar colas y límites de redención.
   - Aporte: diseñar señales y reglas transparentes de liquidez sin prometer paridad incondicional.

## Controles

Documentar derechos legales subyacentes, custodia, oráculos, validadores, puentes, costos de red y escenarios de recuperación. Los indicadores on-chain son señales parciales, no prueba automática de solvencia o identidad.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Cada idea incluye una referencia y una contribución propuesta; falta precisar su prueba de falsación.

- **1. Profundidad de libro observada como proxy de liquidez.** Base: Estimar capacidad de redención incorporando concentración, colas y mercados fragmentados. **Innovación a probar:** Contrastar descuento de salida y absorción de órdenes frente a profundidad simple bajo corridas simuladas. **Prueba decisiva:** pendiente de definir.
- **2. Ratio estático de reservas sin calendario de liquidación.** Base: Reserva optimizada por vencimiento, haircut, correlación y retiros estocásticos. **Innovación a probar:** Probar cobertura por horizonte y costo de oportunidad contra ratio fijo, incluyendo ventas forzadas. **Prueba decisiva:** pendiente de definir.
- **3. Heurística de etiquetar wallets como entidades.** Base: Grafo con incertidumbre de atribución y propagación explícita de confianza. **Innovación a probar:** Validar precisión con etiquetas verificadas y reportar sensibilidad de concentración a falsos enlaces. **Prueba decisiva:** pendiente de definir.
- **4. Factoring/titularización tradicional con documentación fuera de cadena.** Base: Flujos con derechos, waterfall y conciliación on/off-chain instrumentados. **Innovación a probar:** Comparar costo/tiempo de conciliación y recuperación ante errores con proceso tradicional equivalente. **Prueba decisiva:** pendiente de definir.
- **5. Promesa de redención a la par o pausa discrecional.** Base: Mecanismo de cola/regla de liquidez previamente especificado con escenarios de congestión. **Innovación a probar:** Evaluar ejecución contractual y contención de retiros sin asumir que el token conserva paridad. **Prueba decisiva:** pendiente de definir.
