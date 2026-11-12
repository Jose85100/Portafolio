# Equivalencias de campos para integrar fuentes

Las plantillas utilizan nombres de negocio en español. Esta tabla facilita adaptar extractos de versiones anteriores o sistemas que utilicen nombres distintos. Es una correspondencia de nombres, no una certificación de que dos fuentes tengan el mismo grano o significado.

| Nombre anterior | Nombre del laboratorio | Significado a verificar |
|---|---|---|
| `loan_key` | `id_credito` | Identificador estable de la operación o cuenta. |
| `merchant_key` | `id_comercio` | Identificador del comercio asociado cuando forme parte de la llave del origen. |
| `client_id` | `id_cliente` | Identificador estable de la persona o cliente. |
| `loan_id` | `referencia_credito` | Referencia adicional de crédito; puede diferir de la llave técnica. |
| `advance_id` | `id_avance` | Identificador único del evento de avance. |
| `transaction_id` | `id_transaccion` | Identificador único de transacción. |
| `terminal_id` | `id_terminal` | Identificador de terminal. |
| `policy_id` | `id_politica` | Identificador de política o regla. |
| `date_key` | `clave_fecha` | Clave de fecha del calendario. |
| `yyyymm` | `periodo_aaaamm` | Mes representado en formato año y mes. |
| `dpd` | `dias_mora` | Días de mora observados en el corte. |
| `mora_maxima_externa_dpd` | `dias_mora_maximos_buro` | Máximo de días en mora externa según buró. |
| `risk_profile` | `perfil_riesgo` | Clasificación de riesgo de la fuente. |
| `credit_version` | `version_credito` | Versión del registro o política de crédito, según la fuente. |
| `monthly_fee_cop` | `cargo_mensual_cop` | Cargo mensual en pesos; confirmar si corresponde a comisión, mantenimiento u otro concepto contractual. |
| `batch` | `lote` | Lote o grupo de procesamiento. |
| `target_ever_gt30_mob2_3` | `evento_mora_mob2_3` | Resultado posterior para el ejemplo de seguimiento desde MOB 1. |
| `fecha_disponibilidad_target` | `fecha_disponibilidad_resultado` | Fecha en que el resultado queda disponible. |

El motor identifica una cuenta mediante `(id_credito, id_comercio)` y resume clientes mediante `id_cliente`. En una institución donde una cuenta no tenga comercio asociado, hay que definir y aprobar una llave equivalente; no se debe inventar o duplicar un identificador para forzar el cruce. La plantilla de avances conserva `id_credito` e `id_cliente`: si `id_credito` no es único en origen, el cruce se detiene hasta confirmar una llave compuesta.

Las funciones del motor usan ahora `horizonte`, `incluir_mob0`, `columna_saldo` y `fecha_asof`; sus tablas devuelven campos como `es_evaluable`, `evento_mora_mayor_30`, `saldo` y `saldo_valido`. El cálculo, la convención de mora y los denominadores no cambian por el renombrado.

Para trasladar una fuente existente, seleccione las columnas equivalentes en una capa de extracción y renómbrelas a este contrato. Verifique tipos, unicidad, relaciones, fecha de disponibilidad y cobertura antes de calcular. Los nombres de tablas y columnas físicas de Athena deben confirmarse con el catálogo autorizado; las consultas del notebook son ejemplos lógicos, no el esquema de una institución.
