# Datos oficiales: curva diaria del Tesoro de EE. UU.

## Fuente y corte

Fuente primaria: [U.S. Treasury, Daily Treasury Par Yield Curve Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?page=0&type=daily_treasury_yield_curve). Los CSV congelados cubren 2024, 2025 y 2026 hasta el 10 de noviembre. La serie utilizada es el plazo constante a 10 años (`10 Yr`), publicado como porcentaje anual.

El manifiesto [`official/manifest.json`](official/manifest.json) guarda fechas, número de observaciones, parámetros analíticos y SHA-256 por archivo original. El procesamiento rechaza esquemas inesperados, duplicados, fechas inválidas y valores no numéricos. Los valores `N/A` se omiten; el análisis requiere al menos 500 observaciones previas a la ventana fuera de tiempo.

## Semántica y uso

La serie oficial es un rendimiento par interpolado para plazo constante, derivado de cotizaciones indicativas bid-side de bonos del Tesoro en el mercado OTC. No es una serie de retornos observados de un bono identificable.

Para ilustrar VaR y Expected Shortfall se aproxima el retorno diario de una posición larga con duración modificada constante de 8 años:

`retorno ≈ −8 × cambio del rendimiento decimal`

La exposición se expresa por USD 1 millón de nocional para facilitar lectura monetaria; los resultados son una **aproximación de P&L por choque de tasa**, no retornos de un instrumento. No incorpora convexidad, cupón/carry, roll-down, flujos, cambios de duración ni riesgo de base.

## Reproducir

Desde la raíz de este proyecto, con NumPy, SciPy y Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_version.py
```

El comando genera la serie de backtest fuera de tiempo, el resumen de excepciones, el manifiesto y las figuras bajo `data/official/` y `reports/figures/`.
