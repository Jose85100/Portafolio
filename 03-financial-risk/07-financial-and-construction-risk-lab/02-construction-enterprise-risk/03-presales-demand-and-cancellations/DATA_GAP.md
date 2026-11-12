# Brecha de datos: preventas, ventas netas y desistimientos

**Estado:** brecha abierta para outcomes comerciales por unidad/proyecto. Revisión: 2026-11-11.

## Qué está disponible públicamente

- DANE CEED tiene microdatos anonimizados de uso público y documenta variables de unidades vendidas y saldo por vender por obra. También publica una serie agregada VIS/No VIS que, desde 2020-III, contiene vivienda culminada sin vender. La serie procesada de saldo está en [el companion CEED de inventario terminado](../07-real-estate-inventory-and-pricing/observed-dane-ceed-unsold-completed-stock/README.md).
- ELIC aporta actividad formal licenciada, pero licencias no son reservas, ventas ni contratos firmados.
- El CEED aporta observaciones de obras dentro de su cobertura estadística. Aun cuando el microdato incluya unidades vendidas o saldo por vender, no equivale a un historial comercial de reservas y contratos por cohorte y no documenta desistimientos/ventas netas como outcomes contractuales.

## Qué falta para validar preventas/cancelaciones

No se identificó una serie pública oficial colombiana que enlace, por unidad y proyecto, preventa o reserva, firma, desistimiento/cancelación, devolución de recursos y exposición en riesgo. La brecha no se resuelve con licencias ELIC, iniciaciones/culminaciones CEED, saldos de vivienda culminada ni precios agregados. Por ello no hay base pública suficiente para validar una tasa de desistimiento, conversión neta, tiempo de venta, recaudo o pérdida de proyecto.

La serie agregada de CEED puede ser una covariable descriptiva de contexto; no se debe usar como etiqueta de cancelación ni como proxy de preventas. Para el companion agregado referido arriba se usó una descarga ordinaria del archivo publicado por DANE, sin acceder a datos restringidos ni automatizar CAPTCHA. La extracción completa de microdatos CEED no es requisito para esta brecha de outcomes contractuales.

## Esquema mínimo de datos autorizados

| Campo | Definición necesaria |
|---|---|
| `project_id` / `unit_id` | Identificadores estables seudonimizados; documentar cambios y duplicados. |
| `municipality`, `housing_type`, `project_stage` | Contexto geográfico, VIS/No VIS, tipología y etapa del proyecto. |
| `available_at`, `reservation_at`, `contract_signed_at`, `delivered_at` | Fechas que definan entrada a oferta, reserva, firma y entrega. |
| `event_type`, `event_at`, `event_reason` | Firma, retiro de reserva, desistimiento, resolución, mora, sustitución de unidad y motivo diferenciados. |
| `contract_value`, `price_changes` | Valor y fechas de modificación, descuentos e incentivos. |
| `payment_amount`, `payment_at`, `refund_amount`, `refund_at` | Recaudo/devolución fechados para calcular exposición neta. |
| `unit_status`, `status_at`, `censoring_at` | Inventario, venta o cancelación, y corte para identificar contratos aún activos. |
| `source_system`, `extract_at`, `definition_version` | Linaje, fecha de extracción y versión del diccionario/regla de negocio. |

## Condiciones de aceptación antes de modelar

1. Autorizar uso y finalidad, minimizar datos personales y aprobar seudonimización, retención y acceso.
2. Fijar qué cuenta como reserva, contrato, venta neta, cancelación y pérdida; resolver reventas de unidades y cambios de proyecto.
3. Conciliar inventario inicial + entradas − ventas/cancelaciones/salidas = inventario final por fecha de corte.
4. Mantener outcomes temporalmente maduros; validar con partición por fecha de firma y horizonte explícito, comparando con una tasa base por cohorte.
5. Exigir revisión independiente de datos, definición de outcome, estabilidad/calibración y criterios de aceptación antes de usar en originación, pricing o provisiones.
