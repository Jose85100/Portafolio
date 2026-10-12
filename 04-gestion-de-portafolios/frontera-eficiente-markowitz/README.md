# Frontera eficiente de Markowitz

Frontera eficiente long-only de cinco activos con optimización de varianza mínima para una malla de retornos objetivo, portafolio de mínima varianza global y portafolio de máximo Sharpe.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scipy
python3 main.py
```

## Resultado de ejemplo

```text
Frontera eficiente (retorno objetivo -> volatilidad):
  retorno 6.201% | volatilidad 6.359%
  retorno 6.804% | volatilidad 6.930%
  retorno 7.407% | volatilidad 8.502%
  retorno 8.010% | volatilidad 10.756%
  retorno 8.612% | volatilidad 13.952%
  retorno 9.215% | volatilidad 17.793%
                 min_varianza  max_sharpe
acciones_local          0.000       0.070
acciones_global         0.108       0.162
bonos_gob               0.823       0.585
bonos_corp              0.000       0.183
commodities             0.069       0.000
min_varianza: retorno 6.201% | vol 6.359% | Sharpe 0.503
max_sharpe: retorno 6.833% | vol 6.971% | Sharpe 0.550
```
