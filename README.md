# Jose Gabriel Orosco Jiménez — Portafolio de proyectos

Proyectos de riesgo de crédito, modelado cuantitativo, portafolios, estrategia y ciencia de datos aplicada a finanzas y economía. El repositorio combina **notebooks extensos con pruebas automáticas**, **motores de decisión en Python** y una **plataforma de riesgo en C++**.

## Arquitectura de investigación

La organización parte de la pregunta científica y el dominio, no de la herramienta. Consulta el [mapa de investigación y migración](RESEARCH_ARCHITECTURE.md) y la [matriz de madurez](PROJECT_MATURITY.md): un README o una propuesta no se presenta como producto terminado.

| Dominio | Contenido |
|---|---|
| [01 · Economics & Econometrics](01-economics-and-econometrics) | Microeconomía, macroeconomía, teoría de juegos, econometría y macrofinanzas (marco y criterios de inclusión). |
| [02 · Mathematics, Statistics & Quant](02-mathematics-statistics-and-quant) | [Métodos cuantitativos](02-mathematics-statistics-and-quant/quantitative-methods) (6 notebooks, incluido un análisis factorial múltiple con datos reales) y [laboratorio multilenguaje](02-mathematics-statistics-and-quant/quant-libraries) (Python, C, C++, R, MATLAB, Julia). |
| [03 · Financial Risk](03-financial-risk) | [Crédito](03-financial-risk/01-credit-risk), [riesgo de mercado y de modelos](03-financial-risk/02-market-and-model-risk), [investigación de liquidez](03-financial-risk/03-market-liquidity-research), propuestas avanzadas y advisory empresarial. |
| [04 · Quant Strategy & Products](04-quant-strategy-and-products) | [Gestión de portafolios](04-quant-strategy-and-products/asset-management) (5 notebooks) y [plataforma de riesgo en C++17](04-quant-strategy-and-products/risk-engines). |
| [05 · AI & Automation](05-ai-and-automation) | Línea de [ingeniería de datos](05-ai-and-automation/data-engineering), con un [MVP ejecutable de plataforma de datos de riesgo](05-ai-and-automation/data-engineering/risk-data-platform): carga incremental, validaciones, trazabilidad y pruebas. |
| [06 · Strategy, Innovation & Leadership](06-strategy-innovation-and-leadership) | [15 motores de decisión](06-strategy-innovation-and-leadership) en Python, [venture capital](06-strategy-innovation-and-leadership/venture-capital) y [liderazgo de datos](06-strategy-innovation-and-leadership/data-leadership) (10 notebooks). |

## Cuatro tipos de proyecto

- **Notebooks (36)** — `notebook.ipynb` con versión ingenua, diagnóstico, mejoras, robustez y límites. Los datos son **sintéticos con verdad conocida**, así que el notebook comprueba si el método recupera la verdad; las cifras de las conclusiones se **calculan desde los datos** (celdas «Lectura») y una sección final de `assert` hace fallar el notebook si un hallazgo deja de cumplirse. Cuando una hipótesis inicial resultó falsa, el notebook lo dice y muestra la corrección. La excepción es el [análisis factorial múltiple](02-mathematics-statistics-and-quant/quantitative-methods/analisis-factorial-multiple-mfa), que usa **datos reales y abiertos** del Banco Mundial.
- **`main.py` (35)** — la versión corta y ejecutable de cada notebook.
- **Motores de decisión (15)** — proyectos 01–15 de la carpeta 06, cada uno con `src/`, `tests/` y `docs/`.
- **Plataforma C++17** — simulación de pérdidas de crédito, riesgo de mercado y flujos de liquidez, con CMake y pruebas.

## Cómo reproducir

```bash
pip install -r requirements.txt

# Para notebooks (incluye el entorno de investigación)
pip install -r requirements-research.txt

# Notebooks: ejecuta los 36 de principio a fin (tarda más de una hora; algunos corren simulaciones largas)
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

## Sobre los datos

Los proyectos con notebook usan **datos sintéticos con semilla fija**, salvo el análisis factorial múltiple (indicadores públicos del Banco Mundial, licencia CC BY 4.0; los archivos están en su carpeta `datos/`). Ningún proyecto contiene datos de clientes ni confidenciales. Los resultados ilustran el método y **no son evidencia de desempeño real**; los motores de la carpeta 06 son prototipos sintéticos y no sustituyen un análisis con datos de compañías reales.

## Otros proyectos

| Proyecto | Área | Descripción | Estado |
|---|---|---|---|
| [JoseData](https://github.com/Jose85100/JoseData) | Ciencia de datos y econometría | Ejercicios y proyectos de machine learning, econometría y optimización de portafolios. | Público |
| Soluciones analíticas | Modelado cuantitativo | Notas analíticas con derivación formal y código de verificación. | En revisión |
| InvesmentOs | Portafolios y riesgo | Herramienta reproducible para guardar precios, monitorear riesgo y proponer una asignación. | En revisión |

Los proyectos marcados como "En revisión" se publicarán cuando termine la revisión de datos sensibles y credenciales.
