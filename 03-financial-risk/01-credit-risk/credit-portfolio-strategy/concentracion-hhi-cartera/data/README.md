# Datos oficiales: distribución de cartera por producto

## Fuente y extracción

El snapshot proviene de la [Superintendencia Financiera de Colombia, Distribución de cartera por producto](https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8), dataset `rvii-eis8` del Portal Nacional de Datos Abiertos. La ficha registra actualización 2026-10-23; el último corte incluido es 2026-08-31. La extracción versionada, hecha el 2026-11-10, conserva registros desde 2024-01-31. Atribución: **Fuente: Portal Nacional de Datos Abiertos, Superintendencia Financiera de Colombia**; revisar los [términos de uso del portal](https://herramientas.datos.gov.co/terminos) al redistribuir.

El análisis solicita filas cuyo `DESC_RENGLON` contiene `TOTAL`, conserva fechas, tipo/código/nombre de entidad, código y nombre de producto, renglón y saldo bruto. La unidad publicada es entidad–producto–corte. `UNICAP` se usa como identificador de producto para evitar separar variantes de texto en descripciones. La llave auditada es `(fecha_corte, tipo_entidad, codigo_entidad, unicap)`.

El snapshot contiene 9.288 filas, 32 cortes mensuales y saldos de 43 entidades a través de productos. Los controles encontraron cero fechas inválidas, saldos no numéricos, saldos negativos, filas ajenas a TOTAL o duplicados de llave. El [manifiesto](official/manifest.json) conserva SHA-256 de fuente y resultado, fechas y conteos de control.

## Métrica y alcance

Para cada producto y corte, el HHI es `10.000 × suma(share_entidad²)`, donde cada share usa saldo bruto de cartera de la entidad dentro del producto. También se calculan número efectivo de entidades y participaciones top 1/top 5.

Esta fuente mide concentración **entre entidades acreedoras**. No identifica clientes, deudores ni sectores. Por ello la aplicación demuestra el cálculo de concentración del sistema por producto, pero no valida HHI por deudor/sector, límites internos, contagio, PD ni pérdidas de una cartera bancaria.

## Reproducción

Desde la raíz de este proyecto, con Python, pandas, NumPy y Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

El flujo vuelve a calcular la tabla por corte/producto, resumen del último corte y figuras desde el snapshot congelado.
