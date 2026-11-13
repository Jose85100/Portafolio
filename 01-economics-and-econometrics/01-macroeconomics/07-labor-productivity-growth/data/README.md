# Datos observados: productividad laboral

## Fuente

Snapshot WDI para Colombia del indicador `SL.GDP.PCAP.EM.KD`, “GDP per person employed (constant 2021 PPP $)”. La definición del Banco Mundial es PIB dividido por empleo total, convertido a dólares internacionales constantes de 2021 mediante PPP. Los metadatos explican que la estimación combina insumos de OIT, División de Población de Naciones Unidas, Eurostat, OCDE y Banco Mundial; es una estimación publicada, no una serie censal de productividad por trabajador.

- Datos API: `raw/wdi-colombia-gdp-per-person-employed.json`, actualización WDI 2026-10-08, 66 filas de respuesta y 35 observaciones no nulas en 1991–2025. SHA-256: `76cf7f6961d2959014ec2170f64e5d2634ea16eae85177a0687b78ae83b6b185`.
- Metadatos API: `raw/wdi-indicator-metadata.json`. SHA-256: `3da99ea8c5e123bfbf9c16dcfdf092608b9c0118916cde7a4ef744353cc09f62`.
- Fuente consultable: [indicador WDI](https://data.worldbank.org/indicator/SL.GDP.PCAP.EM.KD?locations=CO).

El runner comprueba país, indicador, vintage, unicidad, rango positivo y continuidad anual. Deriva el cambio logarítmico año a año y un índice de nivel con 1991 = 100. No descarga nada al reproducir.

## Salidas

- `official/annual_productivity.csv`: niveles, índice y tasas de crecimiento derivadas.
- `official/application_summary.json`: hashes, período, tasas compuestas y limitaciones.

Los datos son actuales a la fecha de actualización declarada. Revisiones futuras del WDI deben guardarse en un snapshot versionado por separado para no modificar silenciosamente los resultados de esta edición.
