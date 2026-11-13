# Snapshot y definición del proxy

## Fuentes

- `raw/banrep-tes-zero-coupon-monthly-2003-2026.xml`: servicio SDMX de BanRep, flujo `DF_TES_MONTHLY_HIST`, serie mensual `IRGBRY10`, TES COP cero cupón a 10 años, en porcentaje. La metodología de la curva emplea Nelson–Siegel y operaciones del mercado local SEN/MEC; ver [documentación de tasas TES](https://www.banrep.gov.co/en/node/41443) y [catálogo de series](https://suameca.banrep.gov.co/descarga-multiple-de-datos/).
- `raw/fred-us-treasury-10y-dgs10-daily.csv`: [FRED `DGS10`](https://fred.stlouisfed.org/series/DGS10), Treasury de EE. UU. constant maturity a 10 años, rendimiento nominal diario. Fuente primaria que FRED identifica: U.S. Department of the Treasury, H.15.

## Definición

`proxy_t = TES10y_COP_t − Treasury10y_USD_t`, en puntos porcentuales. El XML SDMX de BanRep codifica el TES como fracción; el runner multiplica por 100 para expresarlo como porcentaje. Para igualar frecuencia, se empareja la tasa mensual de BanRep con la media aritmética mensual de observaciones hábiles diarias de Treasury. No se interpolan días ausentes ni se rellenan meses. Falta septiembre de 2025 en el flujo TES; el mes se conserva como brecha y no entra en el cálculo. Los dos rendimientos son nominales y se denominan en monedas distintas. El diferencial contiene expectativas de inflación y depreciación, prima cambiaria, tasas monetarias esperadas, prima por plazo, liquidez y riesgo de crédito; por eso es un **proxy de condiciones nominales relativas de financiación**, no una prima soberana pura.

| Archivo | Grano/cobertura | SHA-256 |
|---|---|---|
| TES BanRep XML | Datos mensuales, enero 2003–octubre 2026; snapshot consultado 10-nov-2026 | `1c20f2e7c01c4e4d48c697c19d1836dbd99a88665e677c1b59a95e4e3288c780` |
| Treasury FRED CSV | Datos diarios desde enero 1962; emparejamiento mensual hasta octubre 2026 | `0a19145416475025a3db81f1d24cddde626211cc098ccba2c22c4baf426c5bb4` |

El runner verifica flujo y dimensiones SDMX, unidad, frecuencia, serie, observaciones positivas, duplicados, fechas y columnas. Comprueba la secuencia esperada e informa la brecha sin imputarla. Conserva los archivos fuente y no usa red al reproducir. Ver [salida derivada](official-proxy/monthly_yield_differential.csv) y [resumen con límites](official-proxy/proxy_summary.json).
