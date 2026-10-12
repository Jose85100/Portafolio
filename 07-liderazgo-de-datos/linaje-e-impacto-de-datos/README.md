# Linaje de datos y análisis de impacto

Catálogo mínimo de conjuntos de datos con sus dependencias. Calcula linaje aguas arriba y aguas abajo, orden de ejecución por ordenamiento topológico, detección de ciclos y qué productos se afectan si falla una fuente.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install 
python3 main.py
```

## Resultado de ejemplo

```text
Orden de ejecucion: raw_cartera -> raw_macro -> raw_precios -> limpio_macro -> limpio_precios -> features_riesgo -> modelo_pd -> reporte_riesgo -> tablero_ejecutivo
Aguas arriba de 'tablero_ejecutivo': ['features_riesgo', 'limpio_macro', 'limpio_precios', 'modelo_pd', 'raw_cartera', 'raw_macro', 'raw_precios', 'reporte_riesgo']
Si falla 'raw_macro' se afecta: ['features_riesgo', 'limpio_macro', 'modelo_pd', 'reporte_riesgo', 'tablero_ejecutivo']
Si falla 'raw_precios' se afecta: ['features_riesgo', 'limpio_precios', 'modelo_pd', 'reporte_riesgo', 'tablero_ejecutivo']
Prueba de ciclo: Ciclo detectado en el linaje
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
