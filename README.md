# Jose Gabriel Orosco Jiménez — Portafolio de proyectos

Proyectos de riesgo de crédito, modelado cuantitativo, portafolios, estrategia y ciencia de datos aplicada a finanzas y economía. El repositorio combina **notebooks extensos con pruebas automáticas**, **motores de decisión en Python** y una **plataforma de riesgo en C++**.

## Por dónde empezar

Los trabajos principales para cada perfil profesional. El catálogo completo está más abajo.

| Perfil | Trabajos principales |
|---|---|
| **Riesgo de crédito y dirección de riesgo** | [IFRS 9 con evidencia pública](03-financial-risk/01-credit-risk/credit-risk-products/ifrs9-investigacion-cuantitativa) ([brief](output/pdf/ifrs9-ecl-executive-brief.pdf)) · [Pérdida esperada PD, LGD, EAD](03-financial-risk/01-credit-risk/credit-risk-products/perdida-esperada-pd-lgd-ead) · [Scorecard logístico WoE/IV](03-financial-risk/01-credit-risk/credit-risk-products/scorecard-logistico-woe) · [Matrices de transición y roll rates](03-financial-risk/01-credit-risk/credit-risk-products/matrices-de-transicion-roll-rates) · [Plataforma de datos de riesgo](05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform) ([brief](output/pdf/risk-data-platform-executive-brief.pdf)) |
| **Estrategia, capital y finanzas** | [Venture capital: cap table, cohortes LTV/CAC, fondo, DCF](06-strategy-innovation-and-leadership/venture-capital) · [Gestión de portafolios](04-quant-strategy-and-products/asset-management) · [Capital, tesorería y ALM: ICAAP, ILAAP, asignación de Euler](03-financial-risk/05-enterprise-risk-advisory/02-capital-alm) · [Asignación de cartera por RAROC](03-financial-risk/01-credit-risk/credit-portfolio-strategy/asignacion-de-capital-raroc) |
| **Quant, riesgo de modelos y validación** | [VaR y Expected Shortfall con tres métodos](03-financial-risk/02-market-and-model-risk/var-es-tres-metodos) ([brief](output/pdf/var-es-official-application-brief.pdf)) · [Backtesting Kupiec y Christoffersen](03-financial-risk/02-market-and-model-risk/backtesting-var-kupiec-christoffersen) · [Validación de modelo: Gini, calibración, PSI](03-financial-risk/02-market-and-model-risk/validacion-de-modelo-psi-gini) · [Pérdidas con cópula gaussiana](03-financial-risk/01-credit-risk/credit-portfolio-strategy/copula-gaussiana-perdidas) · [Plataforma de riesgo en C++17](04-quant-strategy-and-products/risk-engines) |
| **Investigación académica** | [Econometría: DiD, IV, RDD, panel, cuantílica](01-economics-and-econometrics/04-econometrics) · [Congelamiento endógeno del crédito](01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze) · [Macrofinanzas: riesgo soberano, liquidez y ciclo de crédito](01-economics-and-econometrics/05-macrofinance) · [Inflación y actividad observadas (IPC e ISE)](01-economics-and-econometrics/01-macroeconomics/03-inflation-expectations-phillips) |

## Arquitectura de investigación

La organización parte de la pregunta científica y el dominio, no de la herramienta. Consulta el [mapa de investigación y migración](RESEARCH_ARCHITECTURE.md) y la [matriz de madurez](PROJECT_MATURITY.md): un README o una propuesta no se presenta como producto terminado.

## Casos ejecutivos destacados

Tres trabajos muestran la pareja de versiones: laboratorio controlado para estudiar la dinámica del método y aplicación observada para evaluar su uso. La [plataforma de datos de riesgo](05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform) publica un snapshot oficial de cartera ICETEX con 1.237 filas en 18 cortes completos, cuarentena del periodo que no concilia, hashes y activación atómica. El [caso IFRS 9](03-financial-risk/01-credit-risk/credit-risk-products/ifrs9-investigacion-cuantitativa) usa las mismas observaciones para seguimiento agregado de mora, sin presentarlas como PD ni ECL; el motor ECL permanece separado hasta disponer de datos autorizados por contrato. [VaR y Expected Shortfall](03-financial-risk/02-market-and-model-risk/var-es-tres-metodos) conserva el laboratorio de estimación y añade un backtest fuera de tiempo sobre cambios oficiales del rendimiento del Tesoro a 10 años. Cada caso ejecutivo incluye arquitectura, trade-offs, límites y brief de una página: [plataforma](output/pdf/risk-data-platform-executive-brief.pdf), [IFRS 9](output/pdf/ifrs9-ecl-executive-brief.pdf) y [VaR/ES](output/pdf/var-es-official-application-brief.pdf). El resto del catálogo mantiene su estado y alcance; las aplicaciones observadas con sus límites se enumeran a continuación.

### Otras aplicaciones observadas

La misma estructura de dos ediciones ya se extendió a otros proyectos aplicados, cada uno con el alcance que permite su fuente:

- [Backtesting VaR](03-financial-risk/02-market-and-model-risk/backtesting-var-kupiec-christoffersen) y [GARCH de mercado](03-financial-risk/02-market-and-model-risk/garch-volatilidad-y-var): choques de tasa del Tesoro de EE. UU. convertidos en P&L proxy por duración.
- [ES ponderado](03-financial-risk/02-market-and-model-risk/weighted-expected-shortfall-audit/observed-treasury-rate-proxy): aplica la cola de masa fraccionaria a la misma serie oficial de choques de tasa; escenario con duración y nocional supuestos, no pérdida real de cartera.
- [ES ponderado sobre TES colombianos](03-financial-risk/02-market-and-model-risk/weighted-expected-shortfall-audit/observed-colombian-tes-rate-proxy): serie diaria de la curva cero cupón COP 10 años de BanRep aplicada a una sensibilidad hipotética; no contiene posiciones ni P&L real.
- [Estrés de tasa](03-financial-risk/02-market-and-model-risk/pruebas-de-estres-escenarios): extremos observados y estrés inverso de un factor; no sustituye escenarios multifactoriales.
- [Volatilidad cambiaria](01-economics-and-econometrics/04-econometrics/06-time-series-volatility): GARCH aplicado a la TRM oficial del Banco de la República.
- [Concentración HHI](03-financial-risk/01-credit-risk/credit-portfolio-strategy/concentracion-hhi-cartera): saldos de la SFC miden concentración entre entidades acreedoras por producto.
- [MFA de indicadores de desarrollo](02-mathematics-statistics-and-quant/quantitative-methods/analisis-factorial-multiple-mfa): WDI del Banco Mundial, con límites de cobertura, imputación y vintages.
- [Pronóstico ARIMA](02-mathematics-statistics-and-quant/quantitative-methods/arima-pronostico) y [validación temporal](02-mathematics-statistics-and-quant/quantitative-methods/validacion-cruzada-temporal): aplicaciones al IPC observado de DANE, con ventanas holdout y comparadores explícitos.
- [Manifiesto de datos SHA-256](06-strategy-innovation-and-leadership/data-leadership/manifiesto-de-datos-sha256): verifica integridad y controles estructurales sobre un extracto observado de IPC; no certifica la calidad de la fuente.
- [Holdout de entidades vinculadas](05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout): prueba con indicadores WDI que la partición aleatoria por fila cruza países entre entrenamiento y evaluación; el agrupamiento por país evita ese cruce en el diseño probado.
- [Inflación de materiales y suministro](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/06-materials-inflation-and-supply-chain): ICOCED de DANE aporta señales observadas para acero, cemento y concreto; no estima sobrecostos de una obra.
- [Pass-through cambiario](01-economics-and-econometrics/01-macroeconomics/05-exchange-rate-pass-through): IPC DANE y TRM BanRep en una regresión descriptiva con sensibilidad; no identifica causalidad.
- [Productividad laboral](01-economics-and-econometrics/01-macroeconomics/07-labor-productivity-growth): serie WDI para Colombia; contextualiza productividad por trabajador, sin atribuir el cambio a IA ni estimar productividad total de factores.
- [Diferencial soberano nominal](01-economics-and-econometrics/05-macrofinance/05-sovereign-yield-spreads): TES 10 años en COP menos Treasury 10 años en USD como proxy de condiciones relativas; no es prima soberana pura.
- [Calidad agregada de cartera](03-financial-risk/01-credit-risk/credit-risk-products/observed-sfc-quality-proxy): indicador histórico SFC de cartera vencida/bruta por entidad y modalidad, como proxy de stock deteriorado; no es PD ni roll-rate.
- [Señal de precipitación NASA POWER](03-financial-risk/01-credit-risk/credit-portfolio-strategy/climate-parametric-pricing/observed-nasa-power-climate-index): diez puntos urbanos, precipitación modelada diaria y comparación de años completos 2020–2025 con referencia 2000–2019; no es pluviómetro, pérdida ni tarifa.
- [Drift PSI/KS sobre inflación](06-strategy-innovation-and-leadership/data-leadership/deteccion-de-drift-psi-ks): cambio descriptivo entre dos ventanas del IPC DANE; no mide degradación predictiva ni drift de una población de clientes.
- [PSI de mezcla de calificaciones SFC](03-financial-risk/02-market-and-model-risk/validacion-de-modelo-psi-gini/observed-sfc-grade-composition): cambio de composición de saldos A–E en crédito rotativo; no es PSI de scores, Gini ni calibración.
- [IRL histórico SFC](03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl): serie mensual por entidad hasta 2022 más tres cortes discontinuos por tipo hasta agosto de 2026; señal de cobertura, no monitoreo actual ni probabilidad de iliquidez.
- [Steering de cartera ICETEX](06-strategy-innovation-and-leadership/16-credit-portfolio-steering-leadership): ranking descriptivo por departamento y fase para priorizar revisión humana de cartera educativa; no valida crédito digital ni deriva límites.
- [Pipeline de edificaciones CEED](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/02-schedule-cost-overrun/observed-ceed-stage-pipeline): área paralizada sobre área censada como señal sectorial en 57 municipios; no mide retrasos contractuales ni pérdidas por obra.
- [Registros SECOP de suspensión/reanudación](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/02-schedule-cost-overrun/observed-secop-work-suspensions/README.md): 314.437 filas reportadas para todo tipo de contrato público en 2020–2025; no está filtrado a obras ni mide duración o atraso.
- [Saldo CEED de vivienda culminada sin vender](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/07-real-estate-inventory-and-pricing/observed-dane-ceed-unsold-completed-stock/README.md): DANE reporta 2.229 unidades en 23 áreas para 2026-II; no incluye preventas, ventas netas por cohorte ni inventario total en construcción.
- [Concentración de proyectos públicos DNP/SGR](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/11-portfolio-project-concentration/observed-dnp-sgr-project-concentration/README.md): HHI de valor por sector, 1.881,94; mide inversión reportada del SGR, no dependencia ni pérdidas entre proyectos.
- [Sensibilidad de NPV con IPVN e ICOCED](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/15-project-npv-at-risk/observed-dane-npv-sensitivity/README.md): 11 ventanas históricas de ocho trimestres aplicadas a flujos hipotéticos; no estima VaR, probabilidades ni NPV de una obra.
- [Linkage SECOP II de garantías y contratos de obra](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/14-surety-performance-bond-risk/observed-secopsurety-works-link/README.md): 1.076 de 50.154 IDs de obra tienen una fila de garantía enlazada en el corte; no demuestra cobertura efectiva, reclamos o pagos.
- [Sanciones SIC en el sector Inmuebles](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/12-construction-quality-warranty-reserves/observed-sic-real-estate-sanctions/README.md): 126 resoluciones únicas, incluidas 16 con alguna conducta etiquetada “Calidad”; no son reclamos ni pérdidas de garantía.
- [Exposición FX/tasa corporativa](03-financial-risk/07-financial-and-construction-risk-lab/01-corporate-financial-risk/02-fx-interest-rate-exposure/README.md): TRM y DTF BanRep aplicadas a saldos hipotéticos; no son posiciones de una empresa.
- [Costo de refinanciación bancario](03-financial-risk/07-financial-and-construction-risk-lab/01-corporate-financial-risk/03-credit-spread-and-refinancing-risk/observed-banrep-commercial-credit-cost/README.md): tasa agregada BanRep sobre créditos comerciales en escenarios hipotéticos; no es spread de bonos ni precio de un emisor.
- [Contexto inmobiliario IPVU](04-quant-strategy-and-products/real-estate-and-mortgages): variación del índice real de vivienda usada de BanRep para contextualizar escenarios de mercado; no sustituye un avalúo individual.
- [Concentración de compraventas SEN](04-quant-strategy-and-products/market-microstructure/sen-cash-concentration): HHI diario por especie en un mes observado; no mide profundidad disponible ni costo ejecutable.
- [Concentración de tenedores TES](03-financial-risk/03-market-liquidity-research/04-espirales-de-liquidez/observed-tes-holder-concentration): HHI mensual entre categorías publicadas por el IRC, 2010–2025; no identifica tenedores finales ni ventas sincronizadas.
- [Escenarios ICOCED para cashflow-at-risk](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/01-project-cashflow-at-risk/observed-icoced-cost-scenarios): variación histórica de costos sectoriales DANE aplicada a un flujo hipotético; sensibilidad condicionada, no frecuencia ni faltante observado de una obra.
- [Cambios trimestrales de precios de vivienda nueva](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/13-real-estate-price-demand-regimes/observed-dane-ipvn-price-regimes): IPVN DANE 2004–2026 con umbral histórico fijado antes de evaluación 2020–2026; no mide ventas, absorción ni resultados de proyecto.
- [Sensibilidad de fondeo a DTF](04-quant-strategy-and-products/treasury-and-alm): cambios observados en una referencia pública aplicados a un saldo hipotético; no estima el costo de una entidad.
- [Sensibilidad DTF de covenant de proyecto](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/05-project-finance-covenants/observed-dtf-covenant-sensitivity): convierte el cambio interanual observado en una sensibilidad DSCR bajo deuda y flujos hipotéticos; no estima probabilidad de incumplimiento.
- [Valoración residencial IVP DANE](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/07-land-acquisition-and-residual-valuation/observed-dane-ivp-residential-valuation): variación 2024–2025 reportada para 22 ciudades; contextualiza valor residencial, no precio de lote ni absorción.
- [Intervalo radicación–acto ANLA](03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/08-permit-regulatory-and-legal-delay/observed-anla-infrastructure-evaluation-actions): eventos de infraestructura en evaluación; describe hitos presentes en el registro, no el tiempo total de licencia.
- [Concentración territorial del valor agregado](01-economics-and-econometrics/04-econometrics/09-spatial-econometrics): distribución municipal observada de DANE; no estima autocorrelación espacial ni causalidad.
- [Calificación agregada por producto SFC](03-financial-risk/01-credit-risk/credit-risk-products/perdida-esperada-pd-lgd-ead/observed-sfc-product-risk-mix): participación D+E entre saldos calificados y cobertura sobre saldo bruto; no mide PD ni valida pérdida esperada.
- [Cambio de mezcla SFC para roll rates](03-financial-risk/01-credit-risk/credit-risk-products/matrices-de-transicion-roll-rates/observed-sfc-grade-mix-shift/results/report.md): compara saldos D+E agregados por producto; no observa transición de una misma cuenta entre periodos.
- [Regímenes por signo del ISE](01-economics-and-econometrics/01-macroeconomics/06-macro-regime-switching): 247 observaciones mensuales DANE, enero de 2006–julio de 2026; episodios de crecimiento interanual negativo, proxy descriptivo y no fecha oficial de recesión ni modelo Markov-switching estimado.
- [Inflación y actividad observadas](01-economics-and-econometrics/01-macroeconomics/03-inflation-expectations-phillips): 247 meses emparejados de IPC e ISE de DANE, con regresión descriptiva HAC y sensibilidad; no estima una curva de Phillips estructural ni causal.
- [Asignación observada de fondos de pensiones](04-quant-strategy-and-products/asset-management/observed-pension-allocation): composición por clase en cuatro perfiles FPO al 31 de julio de 2026; valida ingestión y agregación de pesos, no optimizadores, retornos ni riesgo económico.
- [Tasa reportada en FIC de mercado monetario](04-quant-strategy-and-products/asset-management/metricas-de-desempeno-y-atribucion/observed-fic-performance): serie SFC agregada y ponderada por valor, 2018–2026; describe la tasa EA reportada del subtipo, no retornos diarios ni desempeño de una cartera.

El [archivo de revisiones de I+D](reviews) conserva iteraciones, métodos, decisiones, reproducción y estado de publicación de cada componente.

| Dominio | Contenido |
|---|---|
| [01 · Economics & Econometrics](01-economics-and-econometrics) | 35 laboratorios de macro, micro, teoría de juegos, econometría y macrofinanzas, con experimentos estructurales específicos y sensibilidad reproducible. |
| [02 · Mathematics, Statistics & Quant](02-mathematics-statistics-and-quant) | [Métodos cuantitativos](02-mathematics-statistics-and-quant/quantitative-methods) (6 notebooks, incluido un análisis factorial múltiple con datos reales) y [laboratorio multilenguaje](02-mathematics-statistics-and-quant/quant-libraries) (Python, C, C++, R, MATLAB, Julia). |
| [03 · Financial Risk](03-financial-risk) | [Crédito](03-financial-risk/01-credit-risk), [riesgo de mercado y de modelos](03-financial-risk/02-market-and-model-risk), [investigación de liquidez](03-financial-risk/03-market-liquidity-research), propuestas avanzadas y advisory empresarial. |
| [04 · Quant Strategy & Products](04-quant-strategy-and-products) | [Gestión de portafolios](04-quant-strategy-and-products/asset-management) (6 notebooks) y [plataforma de riesgo en C++17](04-quant-strategy-and-products/risk-engines). |
| [05 · Artificial Intelligence & Computational Systems](05-artificial-intelligence-and-computational-systems) | Línea de [ingeniería de datos](05-artificial-intelligence-and-computational-systems/data-engineering), con un [MVP ejecutable de plataforma de datos de riesgo](05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform): carga incremental, validaciones, trazabilidad y pruebas. |
| [06 · Strategy, Innovation & Leadership](06-strategy-innovation-and-leadership) | [15 motores de decisión](06-strategy-innovation-and-leadership) en Python, [venture capital](06-strategy-innovation-and-leadership/venture-capital) y [liderazgo de datos](06-strategy-innovation-and-leadership/data-leadership) (10 notebooks). |

## Legal Tech colombiano

La nueva línea [07 · Legal Tech](07-legal-tech) contiene doce propuestas M0 de RAG jurídico, filtros temporales, validación de citas, agentes y especificaciones de skills para Colombia. Incluye arquitectura, contratos y evaluación propuesta; todavía no hay componentes ejecutables.

## Revisión semanal

La [revisión del 12–17 de octubre de 2026](reviews/2026-10-12-week/README.md) registra cobertura, desarrollo, resultados y límites. Incluye 35 laboratorios económicos con modelos específicos, ampliación de auditorías y notebooks de sensibilidad para los motores ejecutivos, recuperación durable y núcleo numérico.

## Formatos de trabajo

- **Notebooks (232; inventario al 12 de noviembre de 2026)** — archivos `.ipynb` para derivaciones, diagnósticos, sensibilidad y reproducibilidad. Su base de evidencia varía por proyecto: incluye conjuntos públicos observados, datos controlados para verificar propiedades matemáticas y experimentos de método. Cada conclusión debe leerse junto a la fuente y los límites declarados en su README; las cifras empíricas se calculan desde los datos y no se atribuyen a una cartera real cuando el ejercicio no la observa.
- **`main.py` (40)** — la versión corta y ejecutable de cada notebook.
- **Motores de decisión (15)** — proyectos 01–15 de la carpeta 06, cada uno con `src/`, `tests/` y `docs/`.
- **Plataforma C++17** — simulación de pérdidas de crédito, riesgo de mercado y flujos de liquidez, con CMake y pruebas.

## Cómo reproducir

```bash
pip install -r requirements.txt

# Para notebooks (incluye el entorno de investigación)
pip install -r requirements-research.txt

# Notebooks: ejecuta todos de principio a fin (puede tardar varias horas)
python3 -m unittest tests.test_notebooks -v

# Un solo notebook
python3 -m unittest tests.test_notebooks.PruebasDeNotebooks.test_<ruta_del_notebook>

# Prueba del modelo avanzado de cópulas
python3 -m unittest tests.test_credito_avanzado

# Motores de decisión (como en la integración continua)
for p in 06-strategy-innovation-and-leadership/[0-9][0-9]-*; do python3 -m unittest discover -s "$p/tests"; done

# Plataforma C++
cmake -S 04-quant-strategy-and-products/risk-engines -B build && cmake --build build && ctest --test-dir build
```

La integración continua (`.github/workflows`) ejecuta los motores de decisión en Python 3.11–3.13 y compila la plataforma C++. Los notebooks modificados se ejecutan en cada PR; una regresión integral programada conserva notebooks ejecutados y un manifiesto de resultados como artefactos.

## Fuentes y alcance de la evidencia

Los casos ejecutivos destacados usan datos oficiales observados del ICETEX y conservan la extracción, atribución, fecha de actualización, hashes, transformaciones y controles de calidad. Otros proyectos tienen fuentes y alcances propios, que se indican en sus fichas. Algunos laboratorios incluyen datos controlados o escenarios generados para verificar propiedades computacionales; esa evidencia respalda las pruebas descritas y no se presenta como desempeño de una cartera real. No se incluyen datos de clientes ni información confidencial.

Cuando una aplicación use un proxy, su ficha definirá el constructo aproximado, la fórmula y unidad de análisis, la fuente y el vintage, los supuestos, los sesgos previsibles, las decisiones que puede informar y la evidencia necesaria para validarlo contra el resultado institucional.

## Otros proyectos

| Proyecto | Área | Descripción | Estado |
|---|---|---|---|
| [JoseData](https://github.com/Jose85100/JoseData) | Ciencia de datos y econometría | Ejercicios y proyectos de machine learning, econometría y optimización de portafolios. | Público |
| Soluciones analíticas | Modelado cuantitativo | Notas analíticas con derivación formal y código de verificación. | En revisión |
| InvesmentOs | Portafolios y riesgo | Herramienta reproducible para guardar precios, monitorear riesgo y proponer una asignación. | En revisión |

Los proyectos marcados como "En revisión" se publicarán cuando termine la revisión de datos sensibles y credenciales.

La [revisión del 17–23 de octubre](reviews/2026-10-23-alignment/README.md) distingue inventario, ejecución nueva y evidencia histórica; incluye dos arquitecturas de decisiones estructuradas en IA y ampliaciones de los cinco MVP del día.

La [revisión académica de los desarrollos del 23 de octubre](reviews/2026-10-23-academic/README.md) vincula 16 referencias publicadas, siete ampliaciones ejecutadas y 24 ideas adicionales con criterios de cierre.
