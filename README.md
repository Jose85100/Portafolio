# Jose Gabriel Orosco Jiménez — Portafolio de proyectos

Proyectos de riesgo de crédito, modelado cuantitativo, portafolios y ciencia de datos aplicada a finanzas y economía.

## Arquitectura de investigación

La organización científica propuesta parte de economía, macroeconomía, microeconomía, teoría de juegos, econometría, matemáticas, estadística y física aplicada, y se extiende a riesgo financiero, estrategia cuantitativa, IA y automatizaciones. Consulta el [mapa de investigación y migración](RESEARCH_ARCHITECTURE.md). Los proyectos históricos fueron reubicados por dominio; el código y los notebooks se preservan. La ejecución de pruebas de integración debe verificarse.

## Áreas

- **Riesgo de crédito y de modelos:** scoring, validación, pruebas de estrés y gobierno de modelos.
- **Modelado cuantitativo y portafolios:** optimización, medición de riesgo y análisis de escenarios.
- **Ciencia de datos y econometría:** machine learning, deep learning y análisis econométrico.
- **Investigación aplicada:** modelos analíticos y reproducibles para problemas de economía y finanzas.

## Carpetas por perfil

- [01 · Riesgo de crédito: productos](03-financial-risk/credit-risk-products)
- [02 · Riesgo de crédito: estrategia y portafolio](03-financial-risk/credit-portfolio-strategy)
- [03 · Riesgo financiero y riesgo de modelos](03-financial-risk/market-and-model-risk)
- [04 · Gestión de portafolios](04-quant-strategy-and-products/asset-management)
- [05 · Cuantitativo y ciencia de datos](02-mathematics-statistics-and-quant/quantitative-methods)
- [06 · Estrategia, innovación y venture capital](06-strategy-innovation-and-leadership/venture-capital)
- [07 · Liderazgo de datos](06-strategy-innovation-and-leadership/data-leadership)

## Cómo está hecho cada proyecto

Cada proyecto tiene tres piezas:

- **`notebook.ipynb`** — el desarrollo completo: versión ingenua, diagnóstico, mejoras, robustez y límites. Los datos son sintéticos y **se conoce el proceso que los genera**, así que el notebook puede comprobar si el método recupera la verdad. Las cifras de las conclusiones se **calculan e imprimen desde los datos** (celdas «Lectura»), y una sección final de **pruebas automáticas** (`assert`) hace fallar el notebook si un hallazgo deja de cumplirse. Cuando una hipótesis inicial resultó falsa al ejecutarla, el notebook lo dice y muestra la corrección.
- **`main.py`** — la versión corta y ejecutable del mismo tema.
- **`README.md`** — qué hace, cómo ejecutar y un resultado de ejemplo.

Para reproducir todo:

```bash
pip install -r requirements.txt
python3 -m unittest tests.test_notebooks -v   # ejecuta los 35 notebooks de principio a fin (tarda: algunos corren simulaciones largas)
```

## Proyectos

> **Sobre los datos:** los proyectos originales reorganizados por dominio usan datos sintéticos con semilla fija para ilustrar el método. No contienen datos de clientes ni confidenciales, y sus resultados no son evidencia de desempeño real.

| Proyecto | Área | Descripción | Estado |
|---|---|---|---|
| [JoseData](https://github.com/Jose85100/JoseData) | Ciencia de datos y econometría | Ejercicios y proyectos de machine learning, econometría y optimización de portafolios. | Público |
| Soluciones analíticas | Modelado cuantitativo | Notas analíticas con derivación formal y código de verificación. | En revisión |
| InvestmentOS | Portafolios y riesgo | Herramienta reproducible para guardar precios, monitorear riesgo y proponer una asignación. | En revisión |

Los proyectos marcados como "En revisión" se publicarán cuando termine la revisión de datos sensibles y credenciales.
