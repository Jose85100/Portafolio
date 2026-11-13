# CVA de contraparte y wrong-way risk

**Estado:** especificación y companion de sensibilidad con factores públicos y exposición construida; CVA real y wrong-way risk permanecen sin validar.

## Pregunta de negocio

¿Cómo cambia la pérdida por riesgo de contraparte cuando la exposición futura positiva, la probabilidad de incumplimiento y la recuperación varían juntas bajo factores comunes de mercado? La respuesta debe poder desagregarse por entidad legal y conjunto de neteo, respetar colateral y términos de cierre, y producir una medida que pueda reconciliarse con valuación y resultados observados. Una serie soberana de CDS, la tasa de cambio, la tasa de política o la calidad de una cartera de préstamos son variables de contexto; por sí solas no responden esta pregunta.

## Formulación objetivo

```text
CVA = LGD × Σ_t DF_t × EPE_t × ΔPD_t
```

Para wrong-way risk, `EPE_t` y `ΔPD_t` deben modelarse con su dependencia condicional a factores comunes, no como promedios independientes. El horizonte, unidad, fecha de valoración, tratamiento de colateral, compensación, riesgo de mercado y definición de default deben fijarse antes de estimar. El companion inferior calcula únicamente una sensibilidad ilustrativa bajo supuestos explícitos.

## Auditoría de fuentes públicas

La búsqueda al 11 de noviembre de 2026 identifica fuentes oficiales pertinentes al contexto, pero ninguna ofrece un panel temporal enlazado de exposiciones, crédito de contraparte, colateral, default y recuperación:

| Fuente | Qué aporta | Por qué no identifica CVA/WWR |
|---|---|---|
| [BanRep, análisis del mercado de CDS soberanos de Colombia, 2026-T3](https://www.banrep.gov.co/en/publications-research/financial-markets-report/box2-third-quarter-2026) | Estudio oficial del mercado soberano de CDS, liquidez, participantes, formación de precios y contenido de riesgo país. | El emisor de referencia es el soberano. El informe es análisis trimestral; no publica en esa página un panel diario abierto de spreads por contraparte, ni exposiciones derivadas o recuperaciones. Un spread soberano no es el spread de una contraparte corporativa o bancaria. |
| [SFC, Distribución de cartera por producto](https://www.datos.gov.co/en/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8) | Publicación mensual de saldo y mezcla de cartera por producto, mora/calificación; aporta contexto de calidad del crédito. | Es cartera de préstamos y deudores reportados; no contiene conjuntos de neteo de derivados, PFE, acuerdos de colateral, valuación close-out ni default/recovery ligados a una contraparte de mercado. |
| [SFC, MURIC](https://www.superfinanciera.gov.co/publicaciones/10116152/sobre-el-muric/) | Describe un reporte regulatorio mensual granular de créditos y deudores, con fechas, garantías, calificación, mora, saldos, PI y PDI. | La descripción corresponde a información de operaciones crediticias. No es un dataset público abierto de trades, CSA, netting sets o pérdidas de contraparte por derivados; no se identificó una descarga pública de esos microdatos. |
| BanRep TRM, IBR/tasas, curva TES, EMBI/CDS soberano | Factores de mercado con frecuencia diaria o mensual según serie. | Un factor común no aporta el lado de exposición ni la probabilidad de default propia de cada contraparte. Correlacionar un factor con un indicador agregado de crédito no valida wrong-way risk. |

Las calificaciones públicas de riesgo país y sus cambios pueden contextualizar el soberano, pero son ordinales y de baja frecuencia; no sustituyen curvas de default o historia de migraciones y pérdidas de la contraparte concreta. No se localizaron spreads CDS corporativos/bancarios colombianos abiertos, con historia fechada, cobertura y metodología suficiente para construir curvas de hazard verificables.

## Contrato mínimo de datos para avanzar

- Identificador pseudónimo estable de contraparte y entidad legal; grupo, moneda, sector y fuente autorizada.
- Operaciones y valuaciones fechadas por netting set; flujos, curvas, escenarios y exposición futura positiva `EPE/PFE` con metodología de pricing versionada.
- Contrato marco, anexo de colateral, jurisdicción, enforceability, umbrales, MTA, frecuencia de margen, disputes, haircuts, moneda y tiempos de liquidación.
- Historial de default y migraciones con fechas, definición del evento, deuda afectada, recuperación/recobro, colateral liquidado y exposición al default; curvas de probabilidad de default por contraparte o fuente de mercado autorizada.
- Factores de mercado sincronizados con valuaciones y eventos crediticios, para estimar dependencia y stress de WWR, con linaje, datos faltantes y controles de timestamp.
- Permisos de uso, reconciliación con contabilidad/CVA desk y resultados de close-out para backtesting independiente.

## Límites, validación y gobierno

Sin netting, colateral, exposición por fecha, default y recovery enlazados, ningún proxy público localizado permite estimar de forma interpretable una CVA o una dependencia wrong-way. No se reportan escenarios monetarios, spreads sustitutos, PD implícitas ni correlaciones como si fueran una pérdida de contraparte. El proxy de CDS soberano es admisible solo como contexto de mercado del soberano; la calidad de cartera SFC solo como contexto agregado de préstamos.

Un desarrollo futuro requiere validación independiente de precios y exposición, reconciliación legal de netting/collateral, pruebas de sensibilidad de PD/LGD, estrés conjunto de exposición y crédito, wrong-way específico y general, estabilidad, backtesting frente a close-outs y límites aprobados por gobierno de modelos. La aceptación y materialidad deben ser fijadas por el dueño del riesgo y el comité MRM. Nada de esto ha sido probado en esta especificación.

## Companion público: sensibilidad ilustrativa de CVA

`public_proxy.py` combina dos series diarias públicas de EE. UU.: [BAA10Y](https://fred.stlouisfed.org/series/BAA10Y), diferencial de rendimiento Baa frente a Treasury a 10 años, y [DGS10](https://fred.stlouisfed.org/series/DGS10), rendimiento Treasury a 10 años. Usa observaciones coincidentes entre 2020 y 2024; el resultado es una serie de valoraciones hipotéticas, no una cartera observada ni evidencia de wrong-way risk.

```sh
curl -L --fail 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAA10Y' -o /tmp/BAA10Y.csv
curl -L --fail 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10' -o /tmp/DGS10.csv
python3 public_proxy.py /tmp/BAA10Y.csv /tmp/DGS10.csv > /tmp/cva_proxy.csv
```

Por cada fecha se supone LGD 60%, EPE constante de USD 1 millón y horizonte de cinco años. El hazard constante se aproxima por spread/LGD; la tasa Treasury a diez años descuenta todos los plazos. Un segundo escenario aumenta EPE 25% por cada 100 puntos básicos de spread sobre 200 pb. Esa relación es impuesta, no estimada; se muestra para explorar sensibilidad conjunta. Los spreads de bonos incluyen componentes distintos al default, no son CDS ni corresponden a una contraparte identificada. No se incluyen netting, CSA, collateral, curva de crédito ni cierres observados. No sirve para inferir una CVA contable o regulatoria ni validar WWR. Las condiciones de uso de Moody's aplican a BAA10Y; el script descarga la serie desde FRED sin redistribuirla.
