# Time Series Volatility: laboratorio y aplicación con TRM oficial

Una mesa con exposición cambiaria necesita anticipar cómo varía su riesgo cuando los movimientos de la tasa de cambio se agrupan en el tiempo. Este proyecto conserva un laboratorio con proceso generador conocido para observar la dinámica de GARCH y suma una aplicación independiente sobre la TRM diaria oficial de Colombia. El modelo GARCH(1,1)-t se estima con datos de Banco de la República hasta 2025-11-21 y se evalúa, sin reestimar, en 252 retornos posteriores. En esa ventana el VaR al 99% registró tres excepciones frente a 2,52 esperadas; el test de cobertura de Kupiec no rechaza la tasa nominal. La muestra es corta para verificar una cola tan extrema, y la TRM es una tasa de referencia, no un precio ejecutable. Por ello el resultado evalúa comportamiento estadístico observado; no valida una estrategia, cobertura o límite institucional.

## Dos ediciones

### Laboratorio controlado

El [notebook reproducible](notebooks/01-estimation-and-robustness.ipynb) genera datos con verdad conocida para estudiar estabilidad `alpha + beta < 1`, recuperación de parámetros y pronóstico bajo sus supuestos. Es el espacio para observar la dinámica teórica y el comportamiento de estimación.

### Aplicación observada

- [Informe de aplicación, decisiones y limitaciones](reports/official-application-2026-11-10.md)
- [Runner reproducible](official_application.py)
- [Snapshot oficial y semántica](data/README.md)
- [Resumen del backtest](data/official/application_summary.json)
- [Pronósticos diarios](data/official/garch_trm_forecasts.csv)
- [Figura del holdout](reports/figures/trm-garch-var99.png)

Desde la raíz del proyecto, ejecutar con `arch`, NumPy, SciPy y Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

## Aplicación y límites

El companion observado filtra las 2.506 filas SDMX congeladas a 1.790 niveles de lunes a viernes y estima sobre 1.537 retornos. El holdout va de 2025-11-24 a 2026-11-10. Los parámetros se estiman una vez y la varianza condicional se actualiza con cada retorno observado. Hay 3 excepciones en 252 días (2,52 esperadas); el p-valor de Kupiec UC es 0,768.

No se rechaza cobertura en esta ventana, pero pocas excepciones dan baja potencia. La TRM es una referencia diaria COP/USD, no cotizaciones ejecutables; el análisis no valida rentabilidad, efectividad de cobertura ni VaR para posiciones reales. Antes de uso de límites se requieren precios transables, exposiciones, reglas de recalibración, pruebas de independencia, estrés y revisión independiente.

## Pregunta de investigación
Heterocedasticidad condicional. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
sigma_t^2=omega+alpha eps_(t-1)^2+beta sigma_(t-1)^2
\]

## Estrategia econométrica
Estabilidad alpha+beta<1 y predicción. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Riesgo macrofinanciero.


El laboratorio controlado y la aplicación observada son evidencias complementarias: la primera verifica propiedades bajo un proceso definido; la segunda evalúa una serie oficial con un holdout real y explicita los límites del factor observado.
