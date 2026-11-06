# Auditoría ejecutada de fuentes canónicas de Drive — 2026-11-05

**Evidencia:** los dos ficheros originales se obtuvieron en modo solo lectura mediante el conector autorizado de Google Drive, sin publicar los raws en GitHub. Los resultados siguientes se calcularon a partir de esos archivos locales. Los comandos de CLI nuevos fueron implementados después; su funcionamiento en CI se comprueba por separado con fixtures.

## SFC: distribución de cartera por producto / mora

- Origen en Master_DATOS: `sfc_distribucion_cartera_producto_riesgo_mora.csv`; ID de Drive `11i_8dCzzIq9L6ktpMi0_NkzGKEsNgk8T`.
- Tamaño: 26.835.118 bytes. SHA-256: `8288c267d67c87f44060088e8392e660d91f7c93532cdd84ea1ccc0c364e21d9`.
- Filas: **111.787**; cortes de **2015-01-31 a 2026-07-31**; **139 fechas**; **32 descripciones de producto (`DESCRIP_UC`)**.
- Clave de investigación: `TIPO_ENTIDAD`, `CODIGO_ENTIDAD`, `FECHA_CORTE`, `UNICAP`, `RENGLON`; **110.793** claves distintas, **994** claves duplicadas con **994 filas excedentes** (0,889 %). Sus valores son conflictivos: no se permite `drop_duplicates` indiscriminado.
- La fuente tiene renglones `TOTAL` y renglones de subproducto: **sumarlos juntos duplica exposiciones**. Las columnas de mora contienen buckets alternativos o solapados; no sumar todas sin un contrato de modalidad y un árbol de renglones.
- Los clientes con mora >30 días son **stock de cuentas/personas en mora**, no default a 12 meses ni transición PD.
- **Dictamen:** INSPECCIONADO, NO APROBADO para agregación productiva ni calibración individual. Siguiente paso: investigar las 994 colisiones por entidad/periodo/renglón y construir la jerarquía completa de categorías.

## InvestmentOS: market_data.sqlite

- Origen Master_DATOS/InvestmentOS, ID Drive `1SHpuLhHA9qfIq-q_-I8Lt-ggupnQ6Acs`.
- Tamaño: **172.044.288 bytes**. SHA-256: `2cc985fb9cad8f16f79c01270674b81f6a8f9e527e822ac7f20a7e6547fdfccb`.
- Esquema: tabla `prices` (símbolo, fecha, OHLC, `adjusted_close`, volumen, fuente, fecha de actualización) y `macro_observations` (indicador, fecha, valor, unidad, fuente, actualización).
- **968.115** precios, **151** símbolos, entre **1970-01-02** y **2026-09-10**, más **20.684** observaciones macro.
- `adjusted_close`: 0 faltantes en la instantánea; **7.997** filas incumplen una o más relaciones OHLC (0,826 %), concentradas en **21 símbolos**, especialmente activos no estadounidenses, futuros y FX. Es imprescindible evaluar zona horaria, proveedor, split y semántica de cada instrumento antes de excluir o corregir.
- Metadatos de actualización: entre 2026-08-09 y 2026-09-10; **no son datos actualizados a noviembre**.
- Contraste descriptivo: retorno logarítmico diario entre cierres ajustados, volatilidad anualizada `sqrt(252) * desviacion_muestral(r_t)`: SPY 18,55 % (8.461 precios); QQQ 26,87 % (6.919 precios); AAPL 44,32 % (11.528 precios); NVDA 58,95 % (6.951 precios). **No** se consideran VaR verificado, ajuste de delistings, backtest ni recomendación de inversión.
- **Dictamen:** HISTÓRICO REAL INSPECCIONADO; apto para exploración condicionada a validación de ajustes corporativos, calendario por mercado, licencias y frescura. No puede etiquetarse `PRODUCTION_READY`.

## Integración de código publicada en esta rama

- `src/drive_readonly.py`: endpoint Google Drive v3 por ID allowlist con token OAuth de alcance `drive.readonly`, copia en staging privado, SHA256, publicación atómica y control sin fallback anónimo.
- `src/sfc_product_profile.py`: perfil completo de fuente SFC, duplicados por clave y reglas básicas de consistencia.
- `src/market_sqlite_profile.py`: SQLite en modo solo lectura, control de esquema, calidad OHLC, series por activo.
- `tests/test_drive_source_profiles.py`: pruebas de allowlist, colisiones SFC, esquema y cálculo de series.
- `.github/workflows/drive-canonical-source-contracts.yml`: CI sin secretos ni publicación de originales.

## Límite de conexión automática

El conector de Drive disponible en esta conversación permitió consultar los originales, pero no instala credenciales OAuth en GitHub Actions por sí solo. Para ejecutar la descarga desde GitHub se necesitará **un mecanismo autorizado de identidad** (token de corta vida o workload identity con permisos mínimos, sin guardar tokens en el repo). Hasta entonces, el ejecutor se usa en entorno autorizado y el CI de GitHub solamente prueba contratos con fixtures. No se asume integración continua de extremo a extremo en producción.

**Gobierno:** Master_DATOS mantiene raw y vintages; Portafolio conserva código, referencias, hashes y resultados derivados. La descarga nueva no altera Drive y no incluye operaciones de escritura.

## Backtesting empírico de VaR y ES (implementación adicional)

Se implementó `src/observed_market_var.py`: rentabilidades logarítmicas con `adjusted_close`, ventana móvil de 250 observaciones exclusivamente anteriores a cada día, VaR histórico al 99 %, ES empírico de cola y prueba de cobertura incondicional de Kupiec. El cálculo exploratorio se reprodujo directamente sobre la misma SQLite real de Drive (no es ejecución certificada de GitHub Actions sobre el archivo privado).

| Instrumento | Backtests diarios | Excepciones | Frecuencia | Último VaR 99 % | Último ES 99 % | Kupiec p |
|---|---:|---:|---:|---:|---:|---:|
| SPY | 8.210 | 117 | 1,425 % | 2,057 % | 2,470 % | 0,000274 |
| QQQ | 6.668 | 96 | 1,440 % | 3,348 % | 3,934 % | 0,000710 |
| AAPL | 11.277 | 156 | 1,383 % | 5,127 % | 6,360 % | 0,000110 |

**Interpretación:** Para estos activos y esta especificación, la hipótesis de una tasa de excepciones del 1 % es rechazada por Kupiec al 5 %. Un modelo construido con datos observados **no es automáticamente un modelo bien calibrado**. La muestra incluye regímenes heterogéneos y los precios ajustados/no ajustes corporativos requieren revisión. No se aplicaron umbrales Basel de traffic light, independencia de excepciones ni validación condicional; agregar Christoffersen, ES backtests y ventanas/regímenes como siguiente iteración. Las cifras de VaR/ES son pérdidas aproximadas en retorno logarítmico, no porcentajes monetarios P&L ni precios actuales.
