# Quant Strategy & Products

Laboratorio cuantitativo aplicado a estrategias, inversión, valoración, tesorería, seguros, mercados y diseño de productos. **Un quant no se limita al trading**: esta carpeta organiza aplicaciones matemáticas, estadísticas y computacionales a decisiones financieras.

## Mapa de áreas

| Área | Contenido |
|---|---|
| [Asset management](asset-management/) | Optimización y gestión de portafolios. [Cinco nuevas líneas](asset-management/IDEAS.md). |
| [Motores cuantitativos](risk-engines/) | Componentes ejecutables y reproducibles. [Cinco extensiones propuestas](risk-engines/IDEAS.md). |
| [Trading cuantitativo](quantitative-trading/) | Estrategias y evaluación neta de costos. |
| [Derivados y valoración](derivatives-and-pricing/) | Curvas, volatilidad, valoración y cobertura. |
| [Tesorería y ALM](treasury-and-alm/) | Composición de balance, fondeo y decisiones de liquidez. |
| [Seguros y actuaría](insurance-actuarial/) | Tarificación y diseño de seguros. |
| [Pensiones y longevidad](pensions-and-longevity/) | Inversión basada en pasivos, longevidad, retiro y suficiencia previsional. |
| [Productos financieros](structured-products/) | Diseño cuantitativo de productos de ahorro, crédito y cobertura. |
| [Activos digitales](digital-assets-quant/) | Liquidez, reservas y flujos tokenizados. |
| [Microestructura y ejecución](market-microstructure/) | Costos de transacción, impacto, enrutamiento y ejecución. |
| [Optimización financiera](financial-optimization/) | Precios, rentabilidad, asignación de recursos e incentivos. |
| [Finanzas conductuales](behavioral-finance/) | Efectos de atención, hábitos, creencias y presentación de decisiones financieras. |
| [Macrofinanzas](quantitative-macro-finance/) | Transmisión macroeconómica a mercados, deuda soberana y coberturas. |
| [Energía y materias primas](energy-and-commodities/) | Precios, almacenamiento, contratos y coberturas con restricciones físicas. |
| [Inmobiliario e hipotecas](real-estate-and-mortgages/) | Valoración, renta, prepago y financiación inmobiliaria. |
| [Finanzas corporativas y de proyectos](corporate-and-project-finance/) | Capital, valoración, infraestructura y opciones reales. |
| [Datos alternativos y NLP](alternative-data-and-nlp/) | Textos, información alternativa y señales cuantamentales. |
| [Pagos y economía de plataformas](payments-and-platform-economics/) | Tarifas, ruteo, liquidación e incentivos de redes de pago. |

Cada área tiene cinco ideas de investigación descritas con método, pregunta cuantitativa y aporte esperado: **18 áreas y 90 ideas**. Son propuestas; no se presentan como modelos ya construidos.

## Proyectos existentes

- [Motor cuantitativo de riesgo en C++17](risk-engines/): simulación de pérdidas de crédito, riesgo de mercado y flujos de liquidez; CMake y pruebas automatizadas.
- [Rebalanceo por beneficio frente a costo](asset-management/rebalanceo-beneficio-costo/): MVP con solver verificado y comparación de costos, riesgo y rotación bajo resultados sintéticos.

## Frontera con otras áreas del portafolio

- [01-economics-and-econometrics](../01-economics-and-econometrics/README.md) desarrolla teoría económica y econometría general. Macrofinanzas aquí estudia sus implicaciones para mercados, precios y decisiones financieras.
- [03-financial-risk](../03-financial-risk/README.md) mantiene medición, estimación, validación y cumplimiento de riesgos. Estos temas consumen sus medidas como insumos cuando aplica.
- En datos alternativos se estudian NLP y señales financieras; gobernanza de datos, ingeniería de modelos y sistemas de IA se conectan con [05-artificial-intelligence-and-computational-systems](../05-artificial-intelligence-and-computational-systems/README.md).
- Pensiones estudia pasivos previsionales, longevidad y desacumulación; seguros mantiene productos de protección y tarificación actuarial. Las hipótesis conductuales se evalúan con diseños empíricos y métricas de bienestar.

## Estándar transversal

Toda implementación debe declarar datos y licencias, unidades, convenciones, benchmark, supuestos, validación temporal o escenarios, costos, sensibilidad y limitaciones. Identificar prototipos como tales; no presentarlos como asesoría de inversión ni como sistemas listos para producción.
