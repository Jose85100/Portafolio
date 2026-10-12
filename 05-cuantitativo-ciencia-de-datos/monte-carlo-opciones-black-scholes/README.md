# Valoración de opciones: Monte Carlo y Black-Scholes

Valoración de una opción call europea con Black-Scholes en forma cerrada y con Monte Carlo (con y sin variables antitéticas), error estándar, convergencia con el número de trayectorias y delta por derivada pathwise.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
Black-Scholes: precio=9.5563 delta=0.5358
        n       tipo  precio_MC   err_std  delta_MC
     1000     simple     9.6277    0.5259    0.5321
     1000 antitetico     9.5213    0.5207    0.5361
    10000     simple     9.4159    0.1628    0.5333
    10000 antitetico     9.4100    0.1650    0.5326
   100000     simple     9.5189    0.0526    0.5349
   100000 antitetico     9.6087    0.0531    0.5353
  1000000     simple     9.5610    0.0167    0.5359
  1000000 antitetico     9.5604    0.0167    0.5360
```
