# Cuantificación actuarial y seguros

Aplicaciones cuantitativas para diseño, tarificación y administración económica de seguros. La implementación debe separar estimación, decisión comercial y requisitos actuariales/regulatorios.

## Cinco ideas

1. **Seguro paramétrico climático para pequeños productores**
   - Modelar pago a partir de lluvia, temperatura o humedad satelital y comparar índices con pérdidas observadas.
   - Núcleo: minimizar riesgo de base entre indemnización paramétrica y pérdida económica; cuantificar asequibilidad y solvencia.

2. **Seguro de interrupción de ingresos para micronegocios**
   - Estimar duración y severidad de interrupciones a partir de eventos observables como cortes de energía, cierres o siniestros cubiertos.
   - Diseñar límites y periodo de espera con simulación de frecuencia-severidad y análisis de selección adversa.

3. **Microseguro de cuotas de crédito**
   - Evaluar protección temporal por incapacidad, hospitalización o pérdida involuntaria de ingresos, coordinada con calendario de pagos.
   - Comparar prima, cobertura y riesgo moral; evitar inferir causalidad de simples correlaciones.

4. **Seguro de bienestar de equipos de pago**
   - Cubrir reparación o reemplazo de terminales POS y pérdida de ingresos por indisponibilidad verificable.
   - Modelar fallas recurrentes, mantenimiento y riesgo de concentración por proveedor o zona.

5. **Reaseguro y pooling paramétrico entre regiones**
   - Diseñar capas agregadas que agrupen riesgos climáticos o catastróficos parcialmente correlacionados.
   - Aporte: estimar beneficio de diversificación, costo de protección y escenarios de riesgo de base entre departamentos.

## Método

Definir evento cubierto, fuente verificable del índice, ventana de medición, exclusiones, curvas de pérdida, prima pura, gastos y margen. Evaluar equidad, explicabilidad, acumulación y riesgo de base.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Umbral climático único o índice de precipitación simple.** Base: Índice paramétrico multi-señal que minimiza riesgo de base con límites de prima y datos observables. **Innovación a probar:** Comparar pérdida no cubierta, prima y cobertura por zona frente al índice simple; validar con pérdidas independientes. **Prueba decisiva:** undefined
- **2. Cobertura indemnizatoria genérica de interrupción.** Base: Pago verificable por duración/severidad del evento con espera, límites y riesgo de dependencia. **Innovación a probar:** Evaluar calibración de frecuencia-severidad, selección adversa y beneficio neto frente a póliza estándar. **Prueba decisiva:** undefined
- **3. Prima plana y beneficio desvinculado del calendario de deuda.** Base: Diseñar cobertura alineada a cuotas y periodos de incapacidad/pérdida de ingreso. **Innovación a probar:** Probar suficiencia de pago y asequibilidad contra cobertura plana, incluyendo riesgo moral y exclusiones. **Prueba decisiva:** undefined
- **4. Garantía de equipo con pago por avería aislada.** Base: Modelar indisponibilidad, mantenimiento, pérdida de ventas y dependencia del proveedor en un mismo contrato. **Innovación a probar:** Comparar costo total y tiempo de recuperación con garantía estándar y mantenimiento preventivo. **Prueba decisiva:** undefined
- **5. Reaseguro por región o capa sin pooling optimizado.** Base: Pool con correlación espacial, bases paramétricas y asignación de capas según contribución marginal. **Innovación a probar:** Mostrar reducción de capital/prima manteniendo solvencia en eventos regionales correlacionados. **Prueba decisiva:** undefined
