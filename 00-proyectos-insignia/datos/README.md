# Capa de datos compartida

`construir_datos.py` descarga y normaliza las fuentes oficiales que usan los cuatro proyectos. Los crudos de datos.gov.co
(~350 MB) no se versionan; `procesados/manifiesto.json` registra la URL, el número de filas y el SHA-256 de cada crudo y de
cada archivo procesado, con fecha de extracción 2026-11-12.

| Archivo procesado | Fuente | Grano | Cobertura |
|---|---|---|---|
| `cartera_sfc_mensual.csv.gz` | SFC, cartera por calificación y altura de mora (datos.gov.co `rvii-eis8`) | entidad × producto × mes | 2015-01 a 2026-08 |
| `tasas_desembolsos_semanal.csv.gz` | SFC, tasas activas y montos desembolsados (`yvb2-ppaa`) | entidad × modalidad × plazo × semana | 2002-05 a 2022-06 |
| `usura_por_modalidad.csv` | SFC, interés bancario corriente certificado (`pare-7x5i`); usura = 1,5 × IBC | modalidad × vigencia | 2007-04 a 2026-11 |
| `macro_mensual.csv` | BanRep, tasa de política (serie 59); DANE, GEIH (desocupación nacional), IPC e ISE | mes | 2005 a 2026 |

## Reglas de construcción y controles

- **Una fila total por producto.** Tarjeta, libranza, construcción y leasing traen subrenglones; se conserva el total y se
  eliminan duplicados por grafía.
- **Mora.** `mora30` suma todos los tramos vencidos; `mora90` suma los tramos que empiezan en el tercer mes o después. En
  vivienda el primer tramo es de 1 a 4 meses, así que su `mora90` es en realidad mayor a 120 días (más estricta).
- **Reconciliación.** Vigente + vencida debe igualar el saldo; el 99,96% de las filas cuadra al 1%, y la columna
  `reconcilia` marca las que no.
- **Unidades.** Los montos de `yvb2-ppaa` vienen en miles de pesos; el techo de usura viene como texto con `%`.
- **Tramos del techo.** Cada semana toma el techo vigente en su fecha de corte.

## Límites

La cartera es agregada por entidad: no hay créditos individuales. El índice de cartera vencida se mueve con castigos y
ventas de cartera que la fuente no separa. Las tasas semanales publicadas terminan en junio de 2022.
