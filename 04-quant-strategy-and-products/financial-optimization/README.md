# Optimización financiera y decisiones de negocio

Métodos cuantitativos para asignar recursos entre productos, clientes, canales y capacidades. Esta línea busca mejorar decisiones económicas y no repetir modelos de riesgo de crédito ni reportes de riesgo de 03-financial-risk.

## Cinco ideas

1. **[Rentabilidad económica por cliente y producto](01-rentabilidad-economica-por-cliente-y-producto/README.md)**
   - Integrar ingresos, costos de servicio, fondeo, capital asignado y comportamiento de uso con reglas de atribución explícitas.
   - Aporte: distinguir margen contable de contribución económica incremental.

2. **[Optimización de precios con demanda heterogénea](02-optimizacion-de-precios-con-demanda-heterogenea/README.md)**
   - Estimar curvas de conversión y elasticidad por segmento bajo límites de equidad y transparencia.
   - Optimizar margen o valor de vida esperado y comparar con reglas de precio uniforme.

3. **[Asignación de cupos comerciales bajo restricciones](03-asignacion-de-cupos-comerciales-bajo-restricciones/README.md)**
   - Asignar presupuesto de crecimiento a productos/canales sujeto a capacidad operativa, objetivos y métricas de riesgo provistas por otras áreas.
   - Núcleo: optimización robusta con retornos inciertos y límites verificables.

4. **[Valor de la información en originación](04-valor-de-la-informacion-en-originacion/README.md)**
   - Cuantificar si una fuente adicional (documento, señal de flujo o verificación) cambia decisiones y resultados suficientes para pagar su costo.
   - Método: experimento controlado o simulación de valor esperado de información con costos de falsa aceptación/rechazo.

5. **[Diseño de incentivos para redes de pago](05-diseno-de-incentivos-para-redes-de-pago/README.md)**
   - Optimizar comisiones, recompensas y subsidios entre comercios, adquirentes y usuarios considerando elasticidad y efectos de red.
   - Comparar equilibrio de un lado con modelo de plataforma multi-lado y escenarios de adopción.

## Requisitos

Separar predicción, causalidad y optimización; declarar restricciones comerciales y regulatorias, costos marginales, incertidumbre y efectos distributivos. Usar pilotos o diseños cuasi-experimentales cuando se afirmen impactos causales.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Cada idea incluye una referencia y una contribución propuesta; falta precisar su prueba de falsación.

- **1. Margen contable atribuido con prorrateo de costos.** Base: Contribución económica incremental con costo de servicio, fondeo y capital versionados. **Innovación a probar:** Conciliar a cuentas agregadas y contrastar ranking con cambios marginales observados. **Prueba decisiva:** pendiente de definir.
- **2. Precio uniforme o elasticidad común por segmento.** Base: Optimización con demanda heterogénea y restricciones de transparencia/equidad. **Innovación a probar:** Probar margen incremental contra precio uniforme y límites de daño/abandono en piloto o holdout. **Prueba decisiva:** pendiente de definir.
- **3. Ranking por retorno esperado sin dependencia entre iniciativas.** Base: Cupos asignados con correlación, capacidad y métricas de riesgo recibidas como insumo. **Innovación a probar:** Comparar valor total realizado y violaciones de límites con ranking simple bajo escenarios comunes. **Prueba decisiva:** pendiente de definir.
- **4. Costo de una variable adicional evaluado por juicio o AUC.** Base: Valor esperado de información en términos de decisiones, errores y costo de dato. **Innovación a probar:** Demostrar valor neto positivo frente a no adquirir dato y medir errores por grupo pertinente. **Prueba decisiva:** pendiente de definir.
- **5. Tarifa/subsidio unilateral sin respuesta del otro lado.** Base: Precio multi-lado que modela externalidades y equilibrio de adopción. **Innovación a probar:** Comparar contribución y adopción a nivel red con tarifa base y escenarios de subsidio. **Prueba decisiva:** pendiente de definir.
