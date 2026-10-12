# Research Architecture — Economics, Quant & AI

## Identidad transversal

**Economic Architect · Quant Strategist · AI Architect · Quantitative Researcher.**

La arquitectura está organizada por **pregunta científica y dominio**, no por herramienta, puesto o lenguaje. Matemáticas, estadística, física, econometría y computación son métodos transversales.

## Seis dominios

1. [Economics & Econometrics](01-economics-and-econometrics): microeconomía, macroeconomía, teoría de juegos, econometría, macrofinanzas.
2. [Mathematics, Statistics & Physics-Inspired Quant](02-mathematics-statistics-and-quant): cálculo estocástico, inferencia, optimización, sistemas complejos, física económica.
3. [Financial Risk Research](03-financial-risk): crédito, mercado, liquidez, contagio, IFRS 9, pruebas de estrés.
4. [Quant Strategy & Financial Products](04-quant-strategy-and-products): asset management, trading, derivados, motores cuantitativos.
5. [AI Architecture & Automation](05-ai-and-automation): agentes, RAG, n8n y sistemas de evaluación. Incluye la línea especializada [Data Engineering](05-ai-and-automation/data-engineering/) para pipelines, lakehouse, contratos, calidad y linaje.
6. [Economic Architecture, Strategy & Leadership](06-strategy-innovation-and-leadership): diseño de mecanismos, innovación, VC y gobierno de datos.

## Líneas de investigación prioritarias

| ID | Línea | Dominio | Métodos centrales |
|---|---|---|---|
| ECO-01 | Inflación algorítmica y fijación dinámica de precios | Economía / micro-macro | Juegos dinámicos, Hawkes, redes |
| ECO-02 | Nowcasting y transmisión macroeconómica | Economía / macroeconometría | MIDAS, VAR/BVAR, causalidad |
| ECO-03 | Competencia, contratos y diseño de mecanismos | Economía / micro | Juegos bayesianos, información asimétrica |
| ECO-04 | Macrofinanzas y fragilidad endógena | Economía / macrofinanzas | DSGE heterogéneo, redes, stress |
| MAT-01 | Termodinámica de portafolios de crédito | Matemáticas / física | Entropía, Lyapunov, atractores |
| MAT-02 | Transiciones de fase del default | Matemáticas / física | Bifurcaciones, Markov, cambios de régimen |
| MAT-03 | Neural SDE para derivados | Matemáticas / cuantitativo | Itô, EDE, estimación neuronal |
| STA-01 | Inferencia causal y econometría de alta dimensión | Estadística | DML, paneles, bootstrap |
| RSK-01 | Riesgo sistémico mediante T-GNN | Riesgo | Grafos temporales, contagio |
| RSK-02 | Cobranzas mediante reinforcement learning | Riesgo | MDP, off-policy evaluation |
| RSK-03 | Stress conjunto mercado-liquidez | Riesgo | Monte Carlo, fire sales, redes |
| PRD-01 | Asset management cuantitativo | Productos | Optimización robusta, CVaR |
| AI-01 | Gemelo digital de riesgo | IA / automatización | SDE, nowcasting, orquestación |
| AI-02 | Arquitectura multiagente para investigación | IA / automatización | RAG, evaluación, trazabilidad |

## Migración ejecutada: rutas anteriores → rutas actuales

| Ruta actual | Destino propuesto |
|---|---|
| `01-riesgo-de-credito-productos` | `03-financial-risk/01-credit-risk/credit-risk-products` |
| `02-riesgo-de-credito-estrategia-portafolio` | `03-financial-risk/01-credit-risk/credit-portfolio-strategy` |
| `03-riesgo-financiero-modelos` | `03-financial-risk/02-market-and-model-risk` |
| `04-gestion-de-portafolios` | `04-quant-strategy-and-products/asset-management` |
| `05-cuantitativo-ciencia-de-datos` | `02-mathematics-statistics-and-quant/quantitative-methods` |
| `06-estrategia-innovacion-vc` | `06-strategy-innovation-and-leadership/venture-capital` |
| `07-liderazgo-de-datos` | `06-strategy-innovation-and-leadership/data-leadership` |
| `08-laboratorio-multilenguaje-quant` | `02-mathematics-statistics-and-quant/quant-libraries` |
| `09-riesgo-mercado-liquidez-avanzado` | `03-financial-risk/03-market-liquidity-research` |
| `10-cpp-risk-platform` (PR #4) | `04-quant-strategy-and-products/risk-engines` |

**Estado de la migración:** las nueve carpetas históricas fueron trasladadas a sus destinos en esta rama. Se comprobó el árbol de Git y se localizaron 36 notebooks. La ejecución completa de notebooks y CI sigue pendiente; no se debe afirmar validación empírica por este traslado.

## Estándar mínimo de cada investigación

- `README.md`: pregunta, contribución, estado, resultados, reproducibilidad.
- `theory/`: supuestos, teoremas, demostraciones, identificabilidad.
- `models/`: especificación probabilística, estimadores y calibración.
- `src/`: implementaciones Python/C++/Julia/R/MATLAB según corresponda.
- `experiments/`: escenarios, datos públicos o sintéticos, seeds, ablations.
- `tests/`: invariantes, pruebas estadísticas, benchmarks y validación.
- `paper/`: artículo, referencias y limitaciones.

La estructura interna es un **contrato de organización**, no evidencia de que esos archivos ya existan. No llamar 'publicado' a una formulación teórica ni 'validado' a una simulación sintética.

## Verificación y cierre de migración

1. **Hecho:** mapear archivos y actualizar `tests/test_notebooks.py` para descubrir notebooks recursivamente.
2. **Hecho:** trasladar los nueve árboles de archivos mediante objetos Git; revisar referencias relativas externas aún es necesario.
3. **Hecho:** actualizar el descubrimiento recursivo de notebooks (el repositorio no debe contener entornos virtuales versionados).
4. **Pendiente:** ejecutar notebooks y pruebas Python y comprobar enlaces; C++ pertenece a PR #4, que debe integrarse por separado.
5. **Pendiente:** fusionar después de CI verde y revisión de diferencias.
