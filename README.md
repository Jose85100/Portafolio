# Portafolio de investigación y desarrollo cuantitativo

Trabajo en la intersección de economía, estadística, riesgo financiero e ingeniería de datos. Este repositorio reúne ejercicios reproducibles, prototipos de software y notas de investigación. No todos tienen la misma madurez: algunos permiten ejecutar un modelo completo y otros documentan una hipótesis todavía por contrastar.

## Cómo está organizado

| Área | Contenido |
|---|---|
| [Economía y econometría](01-economics-and-econometrics/) | Micro, macro, teoría de juegos e investigación econométrica |
| [Matemáticas y estadística](02-mathematics-statistics-and-quant/) | Inferencia, simulación, procesos estocásticos y laboratorio multilenguaje |
| [Riesgo financiero](03-financial-risk/) | Crédito, mercado, liquidez, provisiones y validación |
| [Estrategia cuantitativa](04-quant-strategy-and-products/) | Gestión de portafolios y modelos de inversión |
| [IA y automatización](05-ai-and-automation/) | Ingeniería de datos, pipelines y arquitectura de sistemas |
| [Estrategia e innovación](06-strategy-innovation-and-leadership/) | Venture capital, decisiones de negocio y gobierno de datos |

El [mapa de investigación](RESEARCH_ARCHITECTURE.md) explica la relación entre las áreas y separa las líneas propuestas del trabajo ya implementado.

## Qué se puede ejecutar

Los ejercicios de modelado incluyen notebooks y scripts Python. Los cinco proyectos de [ingeniería de datos](05-ai-and-automation/data-engineering/) incorporan módulos Python, esquemas SQL y, en dos casos, programas C++17.

Para ejecutar las pruebas de notebooks:

```bash
pip install -r requirements.txt
python3 -m unittest tests.test_notebooks -v
```

Para ejecutar las pruebas de ingeniería de datos:

```bash
for project in 05-ai-and-automation/data-engineering/0[1-5]-*; do
  python3 -m unittest discover -s "$project/tests" -v
done
```

La ejecución completa puede tardar debido a las simulaciones. Las pruebas automatizadas y el workflow de CI no sustituyen la validación con datos reales.

## Sobre los resultados

Los ejemplos de modelado utilizan datos sintéticos, normalmente con semillas fijas. Son útiles para examinar supuestos, estabilidad y propiedades numéricas; no deben interpretarse como resultados obtenidos de clientes, empresas o mercados observados. Cuando un proyecto solo tiene documentación, se identifica como tal.

## Otros trabajos

- [JoseData](https://github.com/Jose85100/JoseData): repositorio de ciencia de datos y econometría.

## Estado de desarrollo

El código, la documentación y los esquemas de base de datos se revisan por separado. Una integración descrita como futura no se presenta como operativa. Las pruebas de integración, el rendimiento bajo carga y el despliegue productivo siguen siendo tareas pendientes donde así se indique.
