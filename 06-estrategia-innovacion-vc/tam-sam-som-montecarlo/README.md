# Tamaño de mercado TAM/SAM/SOM con incertidumbre

Estimación bottom-up de TAM, SAM y SOM como distribuciones, no como un solo número: Monte Carlo sobre número de clientes, precio, penetración y capacidad comercial, con intervalos y variables que más explican la incertidumbre.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Millones de USD por ano  P10 | P50 | P90
TAM:   143.7 |   208.1 |   300.5
SAM:    47.3 |    81.2 |   132.8
SOM:     0.7 |     1.2 |     1.9
Correlacion absoluta con el SOM:
precio         0.620
capacidad      0.585
penetracion    0.187
elegible       0.078
empresas       0.036
```
