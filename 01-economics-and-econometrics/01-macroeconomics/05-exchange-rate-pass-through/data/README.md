# Datos observados: IPC DANE y TRM BanRep

## Fuentes y congelación

- `raw/dane-ipc-empalme-2003-oct2026.xlsx`: anexo oficial del IPC, hoja `IndicesIPC`, índice nacional total con base diciembre de 2018 = 100. Fuente primaria: [DANE, IPC histórico](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc/ipc-historico). El libro indica actualización de octubre de 2026.
- `raw/banrep-trm-daily-2003-2026-11-10.xml`: flujo SDMX `DF_TRM_DAILY_HIST`, Banco de la República, tasa diaria COP/USD. El extracto descargado el 10 de noviembre de 2026 cubre observaciones hasta el 31 de diciembre de 2025. La guía oficial describe el [servicio SDMX](https://suameca.banrep.gov.co/archivos/webservices/documento_tecnico_ws_consumo_sdmx.pdf).

| Archivo | Observaciones validadas | Cobertura | SHA-256 |
|---|---:|---|---|
| IPC DANE xlsx | 286 meses | 2003-01 a 2026-10 | `4e8366bf2d03d4bdc15d14b1b21b12a6eec6c3695926abd503a430858ef74e2e` |
| TRM BanRep XML | 8.401 días / 276 meses | 2003-01-01 a 2025-12-31 | `a266cbff71efbe48756773670b33e481973d193d239f67b403a5f541408db323` |

El runner verifica dimensiones y valores positivos, duplicados, forma del XML, indicador y cobertura mensual; calcula la media aritmética de la TRM diaria por mes y los cambios logarítmicos del índice IPC y de la TRM. Las diferencias y rezagos solo se forman para meses contiguos. El cruce efectivo termina en diciembre de 2025 porque ese es el último mes disponible en el extracto TRM conservado.

## Variables y archivos derivados

- `official/monthly_panel.csv`: panel mensual emparejado y transformaciones.
- `official/regression_sample.csv`: muestra con términos contemporáneos y rezagos hasta 3 meses.
- `official/application_summary.json`: procedencia, hashes, especificación, estimaciones y límites.

No se consulta la red durante la reproducción. Los archivos guardados son la fuente de la ejecución documentada; una actualización futura debe generar un nuevo snapshot y cambiar su fecha/hash, sin reemplazar silenciosamente esta edición.
