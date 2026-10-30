# Pensiones y riesgo de longevidad

Métodos cuantitativos para acumular, invertir y convertir ahorro previsional en ingresos sostenibles durante la jubilación. La línea integra flujos de aportes y beneficios, mercados y supervivencia; no sustituye cálculos actuariales oficiales ni reglas de cada sistema pensional.

## Cinco ideas

1. **Inversión basada en pasivos previsionales (LDI)**
   - Construir portafolios que cubran flujos de pensión por edad, indexación y moneda, y medir el excedente frente a obligaciones futuras.
   - Comparar inmunización por duración con optimización multi-periodo y escenarios de tasas, inflación, salarios y longevidad.

2. **Cobertura cuantitativa del riesgo de longevidad**
   - Proyectar mejoras de mortalidad y medir el efecto de que los pensionados vivan más de lo previsto en reservas y pagos.
   - Evaluar bonos de longevidad, reaseguro y swaps de mortalidad; medir riesgo de base entre población cubierta e índice de referencia.

3. **Estrategias de retiro y desacumulación**
   - Comparar retiros fijos, reglas dinámicas y anualización parcial para maximizar ingreso sostenible y controlar riesgo de agotamiento del ahorro.
   - Optimizar utilidad intertemporal bajo incertidumbre de rendimientos, inflación, salud, supervivencia y legado; mostrar sensibilidad a preferencias.

4. **Trayectorias de aportes con empleo e ingresos discontinuos**
   - Simular densidad de cotización, pausas laborales, informalidad e ingresos variables para evaluar aportes voluntarios y mecanismos de continuidad.
   - Comparar políticas por suficiencia esperada, costo fiscal y distribución de resultados; segmentar por trayectorias, no solo por salario promedio.

5. **Diseño de fondos generacionales y estrategias por ciclo de vida**
   - Evaluar asignación de activos por horizonte restante, tolerancia a pérdidas y calendario de beneficios; comparar glide paths estáticos y adaptativos.
   - Medir tasas de reemplazo, riesgo de caída cerca de retiro y dispersión entre cohortes bajo retornos secuenciales.

## Requisitos

Separar mortalidad observada, mejoras futuras y supuestos financieros; documentar tablas, horizonte, moneda e indexación. Reportar intervalos y escenarios adversos, además del caso medio. No convertir simulaciones poblacionales en promesas individuales.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Matching por duración o política 60/40.** Base: LDI multi-periodo sensible a inflación, moneda, cohortes y flujos contingentes. **Innovación a probar:** Comparar volatilidad del funded ratio y déficit de pago frente a duration matching bajo escenarios conjuntos. **Prueba decisiva:** undefined
- **2. Tabla de mortalidad determinística y hedge estático.** Base: Cobertura de mejoras de mortalidad con riesgo de base explícito por cohorte. **Innovación a probar:** Cuantificar reducción del error de pasivo y costo de hedge frente a tabla fija y cobertura sin ajustar base. **Prueba decisiva:** undefined
- **3. Regla fija de retiro como 4% real.** Base: Desacumulación adaptativa a longevidad, mercados e ingreso mínimo protegido. **Innovación a probar:** Comparar probabilidad de agotamiento, volatilidad de ingreso y utilidad frente a regla fija en secuencias adversas. **Prueba decisiva:** undefined
- **4. Proyección basada en cotización continua o salario promedio.** Base: Modelar densidad de aportes discontinua y opciones de continuidad/ahorro voluntario. **Innovación a probar:** Medir suficiencia y brechas entre trayectorias frente a promedio estable, sin borrar heterogeneidad laboral. **Prueba decisiva:** undefined
- **5. Glide path estático solo por edad.** Base: Asignación por cohorte que considera secuencia de retornos y proximidad de beneficio. **Innovación a probar:** Evaluar tasa de reemplazo y pérdida al retiro frente a target-date convencional en simulaciones fuera de calibración. **Prueba decisiva:** undefined
