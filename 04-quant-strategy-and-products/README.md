# Quant Strategy & Products

Laboratorio cuantitativo aplicado a estrategias, inversión, valoración, tesorería, seguros y diseño de productos financieros. **Un quant no se limita al trading**: esta carpeta organiza varias aplicaciones de métodos matemáticos y computacionales a decisiones financieras.

## Mapa de áreas

| Área | Contenido |
|---|---|
| [Asset management](asset-management/) | Optimización y gestión de portafolios; ya cuenta con proyectos implementados de Markowitz, Black–Litterman, paridad y rebalanceo. [Cinco nuevas líneas](asset-management/IDEAS.md). |
| [Motores cuantitativos](risk-engines/) | Componentes ejecutables y reproducibles para decisiones financieras. [Cinco extensiones propuestas](risk-engines/IDEAS.md). |
| [Trading cuantitativo](quantitative-trading/) | Construcción y evaluación rigurosa de estrategias netas de costos. |
| [Derivados y valoración](derivatives-and-pricing/) | Curvas, volatilidad, valoración y cobertura. |
| [Tesorería y ALM](treasury-and-alm/) | Composición de balance, fondeo, flujos y decisiones de liquidez. |
| [Seguros y actuaría](insurance-actuarial/) | Tarificación, seguros paramétricos, protección de ingresos y pooling. |
| [Productos financieros](structured-products/) | Diseño cuantitativo de productos de ahorro, crédito y cobertura. |
| [Activos digitales](digital-assets-quant/) | Liquidez, reservas, flujos tokenizados y mecanismos de redención. |
| [Microestructura y ejecución](market-microstructure/) | Costos de transacción, impacto, enrutamiento y calidad de ejecución. |
| [Optimización financiera](financial-optimization/) | Precios, rentabilidad económica, asignación de recursos e incentivos. |

Cada carpeta contiene cinco propuestas con pregunta cuantitativa, método y aporte esperado. Se registran como líneas de investigación, no como modelos ya construidos.

## Proyectos existentes

- [Motor cuantitativo de riesgo en C++17](risk-engines/): simulación de pérdidas de crédito, riesgo de mercado y flujos de liquidez; CMake y pruebas automatizadas.
- [Rebalanceo por beneficio frente a costo](asset-management/rebalanceo-beneficio-costo/): MVP con solver verificado y comparación de costos, riesgo y rotación bajo resultados sintéticos.

## Frontera con riesgo financiero

La carpeta [03-financial-risk](../03-financial-risk/README.md) mantiene los modelos y estudios de medición, estimación, validación y cumplimiento de riesgos. En esta carpeta se estudian estrategias, motores y productos que consumen medidas de riesgo como insumos. Así se evita duplicar modelos de PD/LGD/EAD, VaR, provisiones o validación regulatoria.

## Estándar transversal

Toda implementación debe declarar datos y licencias, unidades y convenciones, benchmark, supuestos, validación temporal o escenarios, costos, sensibilidad y limitaciones. Los prototipos deben identificarse como tales; no se presentan como asesoría de inversión ni como sistemas listos para producción.
