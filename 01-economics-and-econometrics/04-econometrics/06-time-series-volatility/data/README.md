# Aplicación observada: TRM diaria de Colombia

## Fuente y snapshot

La serie proviene del [servicio SDMX de series del Banco de la República](https://suameca.banrep.gov.co/estadisticas-economicas/) y su flujo `DF_TRM_DAILY_HIST`, documentado en la [guía oficial SDMX](https://suameca.banrep.gov.co/archivos/webservices/documento_tecnico_ws_consumo_sdmx.pdf). El archivo original [`banrep-trm-daily-2020-2026-11-10.xml`](raw/banrep-trm-daily-2020-2026-11-10.xml) conserva 2.506 observaciones del 2020-01-01 al 2026-11-10. SHA-256: `1295dda88cb5a808a2adb37ed9c8c4380dc3b1a170d3720dd53f53e8c313f25f`.

La métrica es la TRM en COP por USD. Se retienen fechas de lunes a viernes para evitar representar fines de semana como observaciones de mercado; quedan 1.790 niveles y 1.789 retornos logarítmicos. No se imputan valores ni se interpolan observaciones.

## Uso y límites

El modelo usa `100 × Δlog(TRM)` para ajustar GARCH(1,1)-t. Las tasas de cambio son referencia oficial y no precios ejecutables de una posición. Los resultados son evidencia de aplicación empírica al comportamiento de la serie, no de rentabilidad de una estrategia, efectividad de cobertura, ni calidad de pronóstico en una cartera institucional.

El snapshot se congeló el 2026-11-10 mediante el servicio SDMX histórico de BanRep. La página del portal anunció una migración de API en octubre de 2026; las nuevas extracciones deben cotejarse con la documentación vigente y guardarse como nuevos snapshots, sin sobrescribir este archivo.

## Reproducir

Desde la raíz del proyecto, con `arch`, NumPy, SciPy y Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

El runner valida el contrato SDMX, genera pronósticos rolling fuera de tiempo, resultado de cobertura, manifiesto y figura.
