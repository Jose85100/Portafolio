# Preventas, desistimientos y absorción comercial

**Área:** 02 construction enterprise risk  
**Estado:** diseño cuantitativo / investigación en construcción.

## Problema y objetivo
Modelo de demanda, conversión, cancelaciones y recaudos bajo ciclos inmobiliarios. El resultado debe expresarse como distribución de pérdidas, probabilidad de incumplimiento de umbrales o decisión sujeta a límites de riesgo, no solo como un indicador descriptivo.

## Formulación matemática
```text
NetSales_t = GrossSales_t - Cancellations_t
```
Los parámetros deben estimarse con datos fechados, unidades consistentes y ventanas sin fuga de información futura. Las correlaciones entre choques deben modelarse y someterse a estrés.

## Datos y metodología
Fuentes candidatas: presupuestos y actas de obra, ERP contable, cronogramas, contratos, preventas y desistimientos, curvas de tasas, índices de costos de construcción y estadísticas públicas. Separar claramente datos observados, supuestos y escenarios sintéticos. Evaluar alternativas paramétricas, empíricas y bayesianas según el tamaño de muestra.

### Fuente pública revisada y brecha de validación

DANE publica las [Estadísticas de Licencias de Construcción (ELIC)](https://www.dane.gov.co/index.php/estadisticas-por-tema/construccion/licencias-de-construccion), con frecuencia mensual y agregaciones de metros cuadrados/unidades licenciadas por destino, tipo de licencia, solicitud, clase de construcción y estrato; los resultados también se organizan geográficamente. ELIC sirve para describir actividad edificadora formal aprobada y contexto de oferta. **No registra preventas, contratos de compraventa, desistimientos, ventas netas, recaudos, exposición por proyecto ni cohortes de clientes.** Por tanto, ni sus aprobaciones ni el área licenciada son etiquetas de demanda, y no validan la estimación de cancelación ni la distribución de pérdidas de este proyecto. La cobertura y las revisiones de la serie deben revisarse al combinar municipios o vintages.

El companion [observed-dane-elic-supply-signal](observed-dane-elic-supply-signal/README.md) reproduce un indicador descriptivo de licenciamiento/oferta formal por municipio y destino con el snapshot DANE de agosto de 2026. Sirve para contexto geográfico de oferta; la brecha de datos de ventas y cancelaciones para este proyecto permanece abierta.

También hay indicadores públicos limitados del CEED: sus microdatos anonimizados documentan ventas/saldos por obra y la serie agregada VIS/No VIS publica stock culminado sin vender. El companion [observed-dane-ceed-unsold-completed-stock](../07-real-estate-inventory-and-pricing/observed-dane-ceed-unsold-completed-stock/README.md) procesa esta última. Estas observaciones no reconstruyen reservas, contratos, ventas netas o desistimientos por cohorte. La brecha exacta, los límites de uso y el esquema mínimo están en [DATA_GAP.md](DATA_GAP.md).

La validación requiere un extracto autorizado de ventas por unidad y proyecto, con como mínimo: identificador estable seudonimizado de unidad y proyecto; municipio, tipología y etapa; fechas de disponibilidad, reserva, firma, desistimiento/cancelación y entrega; valor contractual y cambios de precio; pagos y devoluciones con fecha; motivo y estado de cancelación; inventario disponible y reglas de entrada/salida de la cohorte. El diccionario debe distinguir reserva de contrato firmado, y cancelación de resciliación, mora o cambio de unidad. Si el negocio quiere usar señales de entorno, cada proyecto/municipio debe enlazarse con el vintage ELIC disponible en la fecha de decisión, evitando información publicada después de ella.

Antes de modelar, fijar una unidad de riesgo y un horizonte operativo (por ejemplo, contrato firmado–cancelación dentro de 180 días), una fecha de corte y el tratamiento de contratos censurados o todavía activos. Validar con partición temporal por fecha de firma, dejando completos los horizontes de resultado; comparar con la tasa histórica por cohorte y reportar calibración, precisión/recall a capacidad de contacto definida, cobertura y estabilidad por proyecto/municipio. Un indicador ELIC solo puede evaluarse como covariable contextual incremental frente a un baseline sin ELIC; no debe convertirse en outcome ni en sustituto de ventas observadas. Hasta disponer de ese extracto y sus permisos, la aplicación real de preventas/cancelaciones queda pendiente.

## Validación y límites
Backtesting por cohortes, censura, estrés de tasa hipotecaria. Evaluar incertidumbre paramétrica, estabilidad temporal, riesgo de modelo y sensibilidad a valores extremos. No usar en decisiones reales sin validación independiente, controles de calidad y aprobación de gobierno.

## Entregables previstos
Dataset versionado, diccionario de variables, metodología reproducible, motor Python, tests unitarios, validación out-of-time, escenarios y reporte ejecutivo con límites.
