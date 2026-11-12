# Volatilidad GARCH y VaR condicional

Estimación de un GARCH(1,1) con t de Student sobre retornos simulados, comparación de los parámetros estimados con los verdaderos y VaR a un día condicional a la volatilidad pronosticada.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Aplicación oficial: GARCH sobre choques observados de tasa

Se ajusta GARCH(1,1)-t a los primeros 500 cambios del rendimiento oficial del Tesoro a 10 años, expresados como P&L proxy con duración fija de ocho años. Los parámetros quedan fijos y la varianza condicional se actualiza con cada choque realizado en 214 fechas fuera de tiempo (2026-01-06 a 2026-11-10). El VaR promedio al 99% es 0,788% (aprox. USD 7.881 por USD 1 millón) y registra 4 excepciones frente a 2,14 esperadas; Kupiec UC p=0,254. La suma estimada `alpha + beta = 0,9981` indica persistencia muy alta y requiere evaluación de estabilidad.

La prueba tiene baja potencia con pocos eventos. Esto evalúa la mecánica de pronóstico sobre un factor oficial observado; no valida un VaR de instrumento o portafolio. La serie de rendimiento constante no es retorno total de un bono y no incorpora convexidad, carry, roll-down ni riesgo de base.

- [Runner de aplicación observada](official_application.py)
- [Resumen de ajuste y backtest](data/official/garch_summary.json)
- [Figura de volatilidad y VaR](reports/figures/treasury-garch-var99.png)
- [Datos oficiales y semántica](../var-es-tres-metodos/data/README.md)

Para reproducir esta edición desde la raíz del proyecto:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

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

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
