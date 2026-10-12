# Economic Architecture & Strategy

Diseño de sistemas económicos, estrategia empresarial, venture capital, innovación y liderazgo de datos.

## Cinco motores nuevos de decisión estratégica

| Proyecto | Método | Decisión |
|---|---|---|
| [Capital Allocation & Real Options](01-capital-allocation-real-options/) | Árbol binomial y programación dinámica | Invertir o esperar |
| [Market Entry & Strategic Games](02-market-entry-game-theory/) | Nash puro/mixto y dominancia | Entrada y competencia |
| [Venture Portfolio Construction](03-venture-portfolio-construction/) | Monte Carlo y riesgo de cola | Diversificación de inversiones |
| [Data Investment Prioritization](04-data-investment-prioritization/) | Optimización binaria exacta | Presupuesto de iniciativas |
| [Strategic Resilience & Stress Testing](05-strategic-resilience-stress-testing/) | Escenarios y trayectorias de caja | Liquidez y supervivencia |

Los cinco incluyen código Python, pruebas unitarias y notas técnicas con diagramas Mermaid. Son prototipos sintéticos y no sustituyen análisis con datos de compañías reales.



## Sistemas ejecutivos: proyectos 06–10

| Proyecto | Foco de decisión |
|---|---|
| [Capital Allocation & ROIC](06-enterprise-capital-allocation-roic/) | EVA, WACC y asignación de capital |
| [Executive OKR Operating System](07-executive-strategy-okr-operating-system/) | Seguimiento estratégico y alertas |
| [Risk Appetite & Board Reporting](08-enterprise-risk-appetite-board-reporting/) | Límites y escalamiento de riesgo |
| [Unit Economics & Pricing](09-business-unit-economics-pricing/) | Margen, LTV/CAC y pricing |
| [Crisis Management & Recovery](10-crisis-management-recovery-planning/) | Contingencias y trayectorias de liquidez |

Los motores 01–10 incorporan notas de investigación en `docs/RESEARCH_EXTENSION.md` y herramientas transversales de [validación estadística](shared_validation/). Estas notas describen protocolos de contraste y no acreditan experimentos ejecutados.

## Sistemas corporativos: proyectos 11–15

| Proyecto | Foco de decisión |
|---|---|
| [Corporate Strategic Planning](11-corporate-strategic-planning/) | Planeación estratégica corporativa |
| [Balance Sheet & Capital Management](12-balance-sheet-capital-management/) | Balance y gestión de capital |
| [Executive Incentive Design](13-executive-incentive-design/) | Diseño de incentivos ejecutivos |
| [M&A Strategic Synergies](14-ma-strategic-synergies/) | Sinergias estratégicas en M&A |
| [Enterprise Transformation Portfolio](15-enterprise-transformation-portfolio/) | Portafolio de transformación |

Los 15 motores se prueban con `python -m unittest discover -s <proyecto>/tests` (ver los flujos de trabajo en `.github/workflows`).

## Colecciones de notebooks

Dos colecciones de cinco notebooks extensos cada una, con datos sintéticos de verdad conocida y pruebas automáticas internas:

- [Venture capital](venture-capital/): fondo de venture, cohortes y LTV/CAC, TAM–SAM–SOM con Monte Carlo, *cap table* y dilución, valoración DCF por escenarios.
- [Liderazgo de datos](data-leadership/): reglas de calidad de datos, manifiesto SHA-256, detección de drift (PSI/KS), linaje e impacto, priorización de casos de uso.
