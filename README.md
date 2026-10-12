# Jose Gabriel Orosco Jiménez — Portafolio de proyectos

Proyectos de riesgo de crédito, modelado cuantitativo, portafolios y ciencia de datos aplicada a finanzas y economía.

## Áreas

- **Riesgo de crédito y de modelos:** scoring, validación, pruebas de estrés y gobierno de modelos.
- **Modelado cuantitativo y portafolios:** optimización, medición de riesgo y análisis de escenarios.
- **Ciencia de datos y econometría:** machine learning, deep learning y análisis econométrico.
- **Investigación aplicada:** modelos analíticos y reproducibles para problemas de economía y finanzas.

## Carpetas por perfil

- [01 · Riesgo de crédito: productos](01-riesgo-de-credito-productos)
- [02 · Riesgo de crédito: estrategia y portafolio](02-riesgo-de-credito-estrategia-portafolio)
- [03 · Riesgo financiero y riesgo de modelos](03-riesgo-financiero-modelos)
- [04 · Gestión de portafolios](04-gestion-de-portafolios)
- [05 · Cuantitativo y ciencia de datos](05-cuantitativo-ciencia-de-datos)
- [06 · Estrategia, innovación y venture capital](06-estrategia-innovacion-vc)
- [07 · Liderazgo de datos](07-liderazgo-de-datos)

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

> **Sobre los datos:** los proyectos de las carpetas 01 a 07 usan datos sintéticos con semilla fija para ilustrar el método. No contienen datos de clientes ni confidenciales, y sus resultados no son evidencia de desempeño real.

| Proyecto | Área | Descripción | Estado |
|---|---|---|---|
| [JoseData](https://github.com/Jose85100/JoseData) | Ciencia de datos y econometría | Ejercicios y proyectos de machine learning, econometría y optimización de portafolios. | Público |
| Soluciones analíticas | Modelado cuantitativo | Notas analíticas con derivación formal y código de verificación. | En revisión |
| InvestmentOS | Portafolios y riesgo | Herramienta reproducible para guardar precios, monitorear riesgo y proponer una asignación. | En revisión |

Los proyectos marcados como "En revisión" se publicarán cuando termine la revisión de datos sensibles y credenciales.
