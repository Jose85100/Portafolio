# Snapshot de datos observados del ICETEX

## Versión de evidencia pública: 2026-11-10

Esta entrega usa registros **observados y agregados** del conjunto oficial [Comportamiento de Cartera y Crédito](https://www.datos.gov.co/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir), publicado por el Instituto Colombiano de Crédito Educativo y Estudios Técnicos en el Exterior (ICETEX), Vicepresidencia de Crédito y Cobranza. La ficha del portal indicó actualización el **15-oct-2026**; la extracción congelada se descargó el **10-nov-2026**. El grano es fecha de corte × departamento × fase del crédito.

El snapshot bruto conservado es [`raw/icetex-dugh-vkir-2026-11-10.json`](raw/icetex-dugh-vkir-2026-11-10.json). El archivo transformado es [`processed/delinquency_observed.csv`](processed/delinquency_observed.csv), acompañado por [`processed/manifest.json`](processed/manifest.json) y [`processed/rejected_records.json`](processed/rejected_records.json). SHA-256 del archivo de fuente: `b91afdd83dd9738fb0dcd9606f67ecbdff2fd0da2af31138d9aeb68f83867a7e`.

## Calidad, exclusiones y uso permitido

- Fuente: 1.308 filas; 1.240 conciliaron fila por fila; 68 no conciliaron la suma de conteos.
- Las 68 filas inválidas están concentradas en el corte **2025-06-30**. En ese corte, 3 filas adicionales sí conciliaban; se excluyó el corte completo para evitar una partición temporal incompleta. No se imputaron ni repararon cifras.
- Serie publicable para análisis descriptivo: **1.237 filas, 18 fechas completas, 44 departamentos**, desde 2022-03-31 hasta 2026-09-30. Las fases se normalizan a `ESTUDIOS` y `AMORTIZACION` antes de agrupar.
- `creditos_mora_mayor_90d / creditos_total` es una prevalencia agregada de créditos en mora >90 días a la fecha de corte. No es PD individual, probabilidad futura, tasa de transición a default, LGD, recuperación ni ECL.
- El corte observado no informa la fecha histórica en la que cada cifra se volvió disponible. No usar para backtests point-in-time sin vintages de publicación.

El conjunto mide cartera educativa activa del ICETEX; no representa el sistema financiero colombiano ni las carteras de bancos vigilados por la SFC. Los tres registros válidos de 2025-06-30 también quedan fuera de la serie analítica completa; el archivo bruto y el registro de rechazo conservan la evidencia para revisión.

## Licencia y atribución

Los términos del [Portal Nacional de Datos Abiertos](https://herramientas.datos.gov.co/terminos) autorizan el uso y transformación de los datos públicos y solicitan citar **“Fuente: Portal de Datos Abiertos www.datos.gov.co”**, además de informar la fecha de última actualización disponible. Se conserva la entidad publicadora y su fecha de actualización en este README y el manifiesto. Confirmar condiciones específicas de la ficha antes de redistribuir fuera de este repositorio.

## Reproducir desde el snapshot congelado

Desde la raíz del repositorio, con Python 3.13:

```bash
python3 03-financial-risk/01-credit-risk/observed-data-proxies/src/observed_portfolio.py \
  --as-of 2026-11-10 \
  --source-json 03-financial-risk/01-credit-risk/observed-data-proxies/data/raw/icetex-dugh-vkir-2026-11-10.json \
  --source-last-updated 2026-10-15 \
  --output /tmp/icetex-observed-2026-11-10
```

Para extraer la versión actual del API, omitir `--source-json`; la nueva extracción debe archivarse con su propia fecha, hash y metadatos antes de reemplazar esta versión. El snapshot congelado y su manifest permanecen como evidencia de esta edición.
