# Contratos de intercambio

## Principios

- Los contratos se versionan de forma semántica (`major.minor.patch`). Un cambio incompatible incrementa `major`.
- Todo mensaje lleva `contract_version`, `dataset_version`, `model_version`, `run_id` y `synthetic=true`.
- Las tasas se expresan como decimales, no porcentajes. Montos se expresan en la moneda y escala declaradas; para los ejemplos se usa `COP` nominal.
- Un consumidor debe rechazar un contrato desconocido, datos sin semilla/manifiesto, o `synthetic=false`.

## Contrato de entrada: `ExposureSnapshot/v1`

| Campo | Tipo | Regla |
|---|---|---|
| `exposure_id` | UUID | identificador sintético estable |
| `as_of_date` | ISO-8601 date | fecha de foto de cartera |
| `segment_code` | string | catálogo controlado |
| `ead_cop` | decimal | `>= 0` |
| `days_past_due` | integer | `>= 0` |
| `synthetic` | boolean | debe ser `true` en este repositorio |

## Contrato de salida: `RiskEstimate/v1`

| Campo | Tipo | Regla |
|---|---|---|
| `pd_12m` | decimal | `[0,1]` |
| `lgd_downturn` | decimal | `[0,1]` |
| `ead_cop` | decimal | `>= 0` |
| `expected_loss_cop` | decimal | `pd_12m × lgd_downturn × ead_cop`, sujeto a redondeo declarado |
| `model_version` | string | versión inmutable del artefacto |
| `status` | enum | `accepted`, `rejected`, `quarantined` |

El DDL implementa el contrato relacional y la cabecera C++ define el contrato tipado en memoria. Los notebooks deben persistir una corrida solo después de verificar estas invariantes.

El contrato intercambiable está disponible como [JSON Schema 2020-12](v1/risk_estimate.schema.json). La identidad matemática de pérdida esperada se valida por el consumidor o por la restricción SQL, ya que JSON Schema no expresa multiplicación entre propiedades.
