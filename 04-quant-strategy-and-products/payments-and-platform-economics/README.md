# Pagos y economía de plataformas

Modelos cuantitativos para redes de pago, adquirencia y plataformas con varios lados. El foco es economía de tarifas, liquidez y calidad del servicio; modelos de fraude y detección de anomalías se desarrollan en sus líneas específicas de riesgo e IA.

## Cinco ideas

1. **[Economía de tarifas de adquirencia](01-economia-de-tarifas-de-adquirencia/README.md)**
   - Descomponer costos de red, procesamiento, fraude, contracargos y servicio para evaluar tarifas por tamaño y tipo de comercio.
   - Estimar elasticidad de aceptación y abandono; comparar tarifa plana, por volumen y por valor agregado.

2. **[Enrutamiento de pagos por costo y probabilidad de éxito](02-enrutamiento-de-pagos-por-costo-y-probabilidad-de-exito/README.md)**
   - Elegir proveedor o riel según tarifa, latencia, probabilidad de autorización, liquidación y experiencia del usuario.
   - Optimizar costo esperado con restricciones de disponibilidad, límites por proveedor y reglas de contingencia.

3. **[Liquidez y liquidación en una red de pagos](03-liquidez-y-liquidacion-en-una-red-de-pagos/README.md)**
   - Simular obligaciones entre participantes, desfases de liquidación, reservas y colas bajo patrones intradía.
   - Comparar liquidación bruta y neteo sujeto a límites, costos y restricciones operativas.

4. **[Incentivos de plataforma entre comercios y usuarios](04-incentivos-de-plataforma-entre-comercios-y-usuarios/README.md)**
   - Estudiar cómo descuentos, recompensas y comisiones afectan adopción de comercios, actividad de usuarios y valor total de red.
   - Formular un modelo de dos lados y estimar escenarios de equilibrio; distinguir subsidio temporal de rentabilidad sostenible.

5. **[Valor económico de información transaccional](05-valor-economico-de-informacion-transaccional/README.md)**
   - Cuantificar qué mejoras de conciliación, liquidez, segmentación o acceso a capital genera información agregada y autorizada.
   - Evaluar incrementalidad neta de costos de consentimiento, calidad, seguridad y gobernanza; no monetizar datos personales sin base legítima.

## Métricas

Incluir tasa de aprobación, costo por transacción, latencia, disponibilidad, tiempo de liquidación, retención y margen por segmento. Definir claramente denominadores y ventana de medición.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Cada idea incluye una referencia y una contribución propuesta; falta precisar su prueba de falsación.

- **1. Tarifa plana y costo medio contable.** Base: Tarifa marginal por segmento con elasticidad de aceptación y abandono. **Innovación a probar:** Medir margen y retención frente a tarifa plana con holdout o piloto controlado. **Prueba decisiva:** pendiente de definir.
- **2. Ruteo fijo por proveedor o costo anunciado.** Base: Decisión con probabilidad de autorización, latencia, tarifa y capacidad. **Innovación a probar:** Comparar costo exitoso y disponibilidad con ruta fija bajo datos y fallas reservados. **Prueba decisiva:** pendiente de definir.
- **3. Liquidación bruta o neteo sin optimización conjunta.** Base: Neteo condicionado por liquidez, límites bilaterales y horarios. **Innovación a probar:** Cuantificar ahorro de liquidez sin aumentar retrasos/incumplimientos en escenarios de red. **Prueba decisiva:** pendiente de definir.
- **4. Subsidio a un lado de plataforma por regla manual.** Base: Precio bilateral con adopción endógena y elasticidades estimadas. **Innovación a probar:** Validar crecimiento sostenible de ambas partes y contribución total frente al subsidio actual. **Prueba decisiva:** pendiente de definir.
- **5. Monetización abstracta de datos transaccionales.** Base: Uso agregado con consentimiento que resuelve caso de valor concreto y costo de gobernanza. **Innovación a probar:** Demostrar beneficio neto y minimizar datos frente a alternativa sin compartir información. **Prueba decisiva:** pendiente de definir.
