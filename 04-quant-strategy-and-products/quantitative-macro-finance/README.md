# Macrofinanzas cuantitativas

Aplicación de modelos cuantitativos a precios y decisiones financieras condicionados por el ciclo macroeconómico. Esta área se concentra en la transmisión a mercados, monedas y balances; la teoría y econometría macro general permanece en `01-economics-and-econometrics`.

## Cinco ideas

1. **Nowcast macroeconómico con datos de distinta frecuencia**
   - Combinar indicadores mensuales, semanales y diarios para estimar crecimiento e inflación en tiempo real, con vintages históricos para evitar revisiones retrospectivas.
   - Comparar factores dinámicos, MIDAS y modelos bayesianos; evaluar error por fecha de publicación y estabilidad de revisiones.

2. **Prima por plazo y descomposición de curvas soberanas**
   - Separar expectativas de tasas, prima por plazo y componentes de liquidez en curvas de deuda pública.
   - Contrastar modelos afines de estructura temporal con estimaciones simples; analizar sensibilidad ante cambios de régimen y datos escasos.

3. **Mapa de transmisión macro a activos**
   - Estimar respuestas de TES, FX, acciones y crédito a sorpresas de inflación, actividad y política monetaria.
   - Usar estudios de eventos y proyecciones locales; controlar anticipación, calendario de anuncios y simultaneidad.

4. **Cobertura dinámica de exposición macro**
   - Diseñar coberturas para empresas o portafolios expuestos a tasa, inflación y moneda, combinando forwards, swaps y activos líquidos.
   - Optimizar error de cobertura más costos bajo escenarios conjuntos; comparar cobertura fija, mínima varianza y condicionada a régimen.

5. **Deuda soberana y sostenibilidad de mercado**
   - Simular trayectorias de deuda, costo de intereses y vencimientos con tasas endógenas y shocks de crecimiento, inflación y FX.
   - Separar sostenibilidad fiscal de riesgo de refinanciación y liquidez de mercado; documentar supuestos y no tratar escenarios como pronósticos ciertos.

## Estándar

Usar calendarios de publicación, datos punto-en-el-tiempo, ventanas sin fuga de información y benchmarks transparentes. El objetivo es análisis de mercados y decisiones financieras; la investigación de riesgo sistémico y cumplimiento prudencial se mantiene en `03-financial-risk`.

## Aporte innovador y contraste con la base

Aplicar la [metodología común](../METODOLOGIA_BASE_E_INNOVACION.md). Los aportes siguientes son hipótesis por demostrar, no reclamos de novedad confirmados. Para cada idea se especifican baseline, contribución incremental y prueba de falsación.

- **1. Modelo mensual univariado o último dato publicado.** Base: Nowcast de frecuencias mixtas con vintages y retrasos reales. **Innovación a probar:** Validar error y revisión en pseudo-tiempo real contra benchmark autorregresivo. **Prueba decisiva:** undefined
- **2. Expectativas de tasas como descomposición completa.** Base: Separar prima por plazo, liquidez y expectativas con incertidumbre de identificación. **Innovación a probar:** Probar estabilidad y capacidad explicativa en vencimientos/períodos reservados. **Prueba decisiva:** undefined
- **3. Correlación macro-activo contemporánea.** Base: Respuesta dinámica a sorpresas de anuncio con diseño de evento/proyecciones locales. **Innovación a probar:** Placebos, ventanas alternativas y control de anticipación deben respaldar interpretación causal. **Prueba decisiva:** undefined
- **4. Cobertura fija o hedge ratio incondicional.** Base: Hedge condicionado a régimen macro y covarianza variable con costos. **Innovación a probar:** Comparar error de exposición y costo neto contra benchmark fijo en ventanas out-of-sample. **Prueba decisiva:** undefined
- **5. Proyección de deuda con tasa fija y crecimiento exógeno.** Base: Refinanciación, moneda, vencimientos y tasa endógenos modelados conjuntamente. **Innovación a probar:** Separar métricas de sostenibilidad y rollover; probar escenarios y sensibilidad paramétrica. **Prueba decisiva:** undefined
