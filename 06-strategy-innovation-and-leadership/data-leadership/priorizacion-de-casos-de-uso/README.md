# Priorización de casos de uso de datos

Matriz de priorización de iniciativas de datos con puntaje ponderado de valor (beneficio, ajuste estratégico) y esfuerzo (costo, riesgo, preparación de datos), clasificación en cuadrantes y análisis de sensibilidad a los pesos.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
valor  esfuerzo  prioridad            cuadrante
caso                                                                       
automatizacion de reportes   4.35       1.7       2.56      ganancia rapida
segmentacion de clientes     6.00       2.7       2.22      ganancia rapida
monitoreo de cartera         8.00       3.8       2.11             hacer ya
pronostico de liquidez       6.65       3.4       1.96             hacer ya
scoring de originacion       9.00       5.1       1.76      proyecto grande
deteccion de fraude          7.65       6.1       1.25      proyecto grande
precios dinamicos            6.30       7.1       0.89  descartar o aplazar
chatbot de servicio          4.65       6.0       0.78  descartar o aplazar
Caso en primer lugar bajo pesos aleatorios de valor:
automatizacion de reportes    1.0
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
