# Puntos observados de volatilidad de opciones SPY

El [servicio de cotizaciones diferidas de Cboe](https://www.cboe.com/delayed_quotes/spy/quote_table) publica una cadena de opciones; el script descarga el JSON de su servicio, registra la fecha de consulta y SHA-256 de la respuesta y extrae puntos por strike y vencimiento. Se conservan precios bid/ask e IV publicada por la fuente. Ejecución con Python 3, curl y conexión a internet:

```sh
python3 04-quant-strategy-and-products/derivatives-and-pricing/02-superficie-de-volatilidad-sin-arbitraje/observed_options/download.py
```

El resultado `output/spy_quotes.csv` contiene opciones estándar SPY con bid positivo, ask no inferior al bid, volatilidad positiva y vencimiento posterior al corte. `output/manifest.json` identifica la respuesta capturada; una nueva ejecución sobrescribe los resultados. El hash permite identificar la respuesta, pero su reproducción exacta requiere conservar el JSON original sujeto a las condiciones de uso de Cboe. Consultar dichas condiciones antes de redistribuir datos. La hora es la informada por la fuente; no se asume zona horaria.

Los puntos no constituyen una superficie ajustada ni libre de arbitraje. Pueden estar desactualizados, incluir precios sin operaciones recientes y la IV depende de convenciones de la fuente. SPY es una opción americana con dividendos: su IV no debe tratarse sin ajuste como cotización de una opción europea. El filtrado no comprueba sincronización, liquidez, arbitraje ni calidad de calibración. Falta estimar la superficie y evaluarla fuera de muestra.

Para CVA, estos datos pueden apoyar un ejemplo de exposición a opciones sobre SPY y sensibilidad al mercado. No identifican la probabilidad de incumplimiento, recuperación, colateral, neteo ni dependencia entre exposición y contraparte; por sí solos no validan CVA ni wrong-way risk.
