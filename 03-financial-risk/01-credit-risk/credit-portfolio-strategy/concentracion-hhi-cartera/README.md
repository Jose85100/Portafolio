# Concentración de cartera con HHI

Este proyecto tiene dos ediciones complementarias. El laboratorio controlado muestra cómo el HHI responde a distribuciones conocidas por deudor y sector. La edición oficial aplica la misma estadística a los saldos de los establecimientos por producto y contrasta su uso con datos observados de la Superintendencia Financiera de Colombia.

## Aplicación oficial: concentración de acreedores por producto

El snapshot de Datos Abiertos de la SFC contiene 9.288 filas de saldo bruto clasificadas como `TOTAL` en 32 cortes mensuales, del 2024-01-31 al 2026-08-31. La edición calcula HHI, número efectivo de entidades, top 1 y top 5 por producto y fecha. En agosto de 2026 el HHI es 2.215 en crédito rotativo, 1.222 en tarjetas, 1.039 en libranza y 1.740 en vivienda VIS en pesos.

Esta aplicación mide concentración **entre entidades acreedoras**, no entre deudores o sectores. Es evidencia oficial para seguimiento de concentración del sistema por producto; no valida límites internos de un banco, EL, PD ni concentración de contrapartes dentro de una entidad.

- [Informe ejecutivo de la aplicación observada](reports/official-application-2026-11-10.md)
- [Fuente, extracción, controles y licencia/atribución](data/README.md)
- [Runner reproducible](official_application.py)
- [Serie HHI observada](reports/figures/sfc-lender-hhi-trend.png)

## Laboratorio controlado

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
HHI por deudor: 0.0081 | numero efectivo de deudores: 124 de 500
HHI por sector: 0.1800 | numero efectivo de sectores: 5.6 de 8
Participacion top 10 deudores: 21.0% | mayor deudor: 3.99%
Participacion por sector:
sector
comercio        0.281
industria       0.206
servicios       0.154
agro            0.126
transporte      0.111
construccion    0.078
energia         0.030
tecnologia      0.016
  mayor deudor <= 5%: CUMPLE
  top 10 <= 25%: CUMPLE
  mayor sector <= 30%: CUMPLE
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
