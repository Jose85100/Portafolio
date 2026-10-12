# Volatilidad GARCH y VaR condicional

Estimación de un GARCH(1,1) con t de Student sobre retornos simulados, comparación de los parámetros estimados con los verdaderos y VaR a un día condicional a la volatilidad pronosticada.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install arch numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
Parametros (estimado vs verdadero):
  omega: 0.023 vs 0.02
  alpha: 0.090 vs 0.08
  beta:  0.884 vs 0.9
  gl:    6.0 vs 6
Volatilidad pronosticada a 1 dia: 0.953% | VaR 99% a 1 dia: 2.452%
```
