# Datos que faltan para sustituir simulaciones — contratos de adquisición

Los datasets de `Master_DATOS` permiten trabajar con series observadas, pero no identifican automáticamente todos los objetivos de los modelos existentes. No crear PD/LGD/EAD a partir de saldos de cartera.

| Dominio / aplicación | Unidad y variables mínimas | Alternativa proxy admisible | Fuente observada existente | Brecha que impide calibración |
|---|---|---|---|---|
| PD individual | cliente-crédito-fecha, score_asof, default_event, default_date, producto, saldo, 12m y censura | UCI Taiwan (impago 1 mes, benchmark extranjero solamente) | UCI PR #152 | etiquetas nacionales y origen longitudinal |
| LGD y EAD | préstamo-mes, EAD al default, disposiciones, colateral, flujos de cobro netos, calendario recuperaciones, costo ejecución | benchmark explícito o análisis de sensibilidad, no LGD real | ninguno adecuado | históricos privados de recuperaciones y utilizaciones |
| IFRS 9 staging | PD en originación, PD actual, días mora, dificultades cualitativas, SICR, EIR, contractualidad | escenarios macro reales con reglas hipotéticas documentadas | BanRep, SFC, DANE | historia contractual y cambios de riesgo por préstamo |
| Riesgo sistémico | banco-producto-corte, saldos, morosidad, capital y fondeo | ratios de stock con hipótesis explícita | SFC bancos_panel y SFC producto/mora | validar método, denominadores y vigencia |
| Riesgo de liquidez / ALM | depósitos por entidad/plazo, vencimientos, tasas, retiros, haircuts | DTF/IBR, saldos y captaciones agregadas | BanRep tasas, SFC nacional | comportamiento efectivo de pasivos y estrés de depósitos |
| Asset management y VaR | precios ajustados, dividendos, eventos corporativos, volúmenes, ticker historizado, calendario de negociación, costos | precios de mercado históricos si licencia permite | market_data.sqlite + manifest InvestmentOS | inspección de esquema, splits y supervivencia; estado 2026-09-10 desactualizado |
| Pensiones | tablas mortalidad por edad/sexo, aportes, salarios, rentabilidad, inflación | DANE proyecciones como hipótesis demográficas | DANE proyecciones, SFC fondos voluntarios | mortalidad y dinámica de aportes no observable por individuo |
| Riesgo climático | lluvia, temperatura, anomalías, mapa peligro, geografía, pérdidas aseguradas | NASA/IDEAM para hazard; sin afirmar siniestralidad | Shadow NASA y clima | historial de siniestros y exposición asegurada |
| Estrategia y empresas | estados financieros, inversión, flujo caja, ingresos y deuda | agregados DIAN/SECOP (contexto, no empresa individual) | ATLAS_EMPRESAS, DIAN, SECOP | estados financieros de firma y denominador negocio |
| RAG legal | texto oficial, jurisdicción, vigencia, versión, autoridad, citas | corpus legal público con etiquetas humanas | fuentes oficiales por integrar | verificación de versiones y permisos |

## Orden de nuevas ingestas

**P0:** auditar `sfc_distribucion_cartera_producto_riesgo_mora.csv`; inspeccionar `market_data.sqlite` y su `latest_data_provenance.json`; descargar series DANE de mercado laboral con publicación y vintage; incorporar fuentes microobservadas con definición de default y censura.

**P1:** panel SFC por entidad y produto, clima IDEAM/NASA + siniestros públicos si existen, series de flujos y ejecución territorial. Para indicadores BanRep ya disponibles, priorizar contract y validación antes de más descargas.

**P2:** fuentes privadas con permiso, NDA y anonimización; no subir PII o datos restringidos a GitHub/Drive público. Simulaciones estructurales deben conservarse en tests, Monte Carlo, stress y experimentos con verdad conocida.

## Requisitos de aceptación de cualquier nuevo dataset

`source_id`, `source_owner`, `source_uri`, `license`, `grain`, `units`, `observation_date`, `published_at`, `retrieved_at`, `vintage`, `version`, `sha256`, `feature_available_at`, esquema versionado, reporte de calidad, recuento nulos/duplicados, transformación reproducible, mapeo de consumidor y pruebas anti-leakage.

**Nota temporal:** Los manifiestos de InvestmentOS leídos hasta ahora fueron producidos el 10 de septiembre de 2026, por lo que sus etiquetas de `fresh` eran relativas a esa fecha. A noviembre de 2026 no equivalen a frescura actual. No promoverlos a producción sin actualización y verificación de mercado.
