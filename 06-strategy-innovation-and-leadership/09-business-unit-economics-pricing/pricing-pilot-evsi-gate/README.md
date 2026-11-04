# Pricing Pilot EVSI Gate

Extensión del motor 09: además de elegir precio con capacidad y CVaR, calcula si conviene pagar por un piloto A/B antes de escalar. Es un modelo finito de valor esperado de información muestral, con datos sintéticos Beta-Binomial y acciones de cierre, precio A y precio B.

## Ejecutar
Desde esta carpeta: `bash run.sh`. Instala `matplotlib==3.9.2`, ejecuta pruebas y genera `results/sensitivity.csv`, `results/summary.json`, `results/net_evsi.png` y notebook ejecutado. Python 3.12.

## Interpretación
El valor de la información no incluye ingresos realizados durante el piloto. `n` es exposición por brazo; la regla compara EVSI contra coste de piloto en unidades de contribución abstractas. La salida es una sensibilidad analítica, no un experimento comercial ni causalidad identificada. Ver `informe.md` y `MVP.md`.
