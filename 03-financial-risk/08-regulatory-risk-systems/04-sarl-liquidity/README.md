# SARL y riesgo de liquidez

**Estado: diseño con prototipo sintético de escalera de caja.** Flujos, activos líquidos, fondeo y contingencia. El prototipo no calcula indicadores regulatorios ni valida el sistema SARL de una entidad.

## Prototipo reproducible: vencimientos y primera insuficiencia

La [escalera de caja](../engines/liquidity_ladder.py) agrega entradas y salidas contractuales por fecha, calcula saldos de cierre y señala la primera fecha con saldo negativo. También identifica el saldo mínimo de cierre, su primera fecha y la financiación inicial mínima que habría evitado saldos negativos de cierre. El [ejemplo](examples/flujos_sinteticos.csv) es enteramente sintético. Ejecutar desde la raíz del repositorio:

```bash
python3 03-financial-risk/08-regulatory-risk-systems/engines/liquidity_ladder.py 03-financial-risk/08-regulatory-risk-systems/04-sarl-liquidity/examples/flujos_sinteticos.csv --as-of 2026-01-01 --through 2026-01-10 --currency COP --opening 100.00
python3 -m unittest discover -s 03-financial-risk/08-regulatory-risk-systems/engines -p 'test_*.py' -v
```

Para el ejemplo: entradas 65.00, salidas 140.00, saldo final 25.00 y primera insuficiencia el 2 de enero, con saldo -10.00. El saldo es de cierre por fecha: no identifica insuficiencias intradía ni presume orden entre flujos de un mismo día. Los identificadores por fecha permiten conciliar el agregado con el archivo fuente.

La financiación inicial mínima es `max(0, -menor saldo de cierre)`: para el ejemplo es 10.00. Supone que se aporta al inicio y permanece disponible sin intereses, costos, restricciones ni cambios en los flujos. Si el mínimo se repite, se informa la primera fecha. No es una recomendación de fondeo ni mide brechas intradía.

**Contrato:** CSV UTF-8 con columnas únicas `flow_id`, `due_date`, `currency`, `amount`; clave `flow_id` única; fecha ISO incluida entre corte y horizonte; una sola moneda identificada con tres letras mayúsculas; importes decimales con máximo dos cifras, positivos para entradas y negativos para salidas. El saldo inicial no puede ser negativo. No se imputan vacíos ni se convierten monedas; las entradas inválidas se rechazan. Se utilizan unidades enteras de centésimas, sin errores binarios de redondeo. Los flujos del corte se aplican después del saldo inicial. El resultado incluye ambas fechas límite incluso sin flujos y puede mostrar saldos negativos para representar el déficit.

**Límites:** no modela activos líquidos, gravámenes, límites de uso, comportamiento de depósitos, haircuts, renovaciones, fondeo contingente, ni métricas IRL/LCR/NSFR. Tampoco valida la procedencia, fecha de disponibilidad, moneda efectiva o completitud económica de los datos: estas comprobaciones son responsabilidad del usuario. Para una aplicación real se requieren contratos point-in-time, escenarios, evidencia de fuente y conciliación con tesorería y las reglas vigentes que correspondan a la entidad.

## Escenarios ilustrativos con escala observada SFC

El [ejercicio con datos SFC](observed-sfc-proxy/) usa ALM y RLN bancarios agregados de agosto de 2026 para escalar una caja y tres salidas **hipotéticas**. Conserva fuente, unidades, hashes, supuestos y resultados reproducibles. No infiere fechas de flujo real a partir de IRL ni valida un SARL institucional.

## Fundamentos

Caja_t = caja_inicial + suma de flujos netos hasta t. Las expresiones son bases de investigación, no sustitutos de anexos regulatorios. Consultar [fuentes y perímetro](../SOURCES.md).

## Datos y contratos

Campos mínimos: flujo contractual, vencimiento, moneda, contraparte, haircut. Declarar grano, moneda, unidades, corte, fecha efectiva, fecha de disponibilidad, licencia, origen y versión. Rechazar duplicados de clave; no imputar cero a datos desconocidos. Separar datos sintéticos de observaciones reales.

## Arquitectura y motor propuesto

Adaptador de fuentes → validación de contratos → selección de reglas por entidad y fecha → motor específico → conciliación → evidencia y revisión humana. Ver [arquitectura transversal](../00-architecture/README.md).

Reutilizar [componentes existentes](../../03-market-liquidity-research/) antes de crear implementaciones paralelas. El motor propuesto debe exponer entradas tipadas, parámetros, resultados desagregados y razones de excepciones.

## Tres líneas de investigación

1. Runoff conductual: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
2. concentración de depositantes: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.
3. reverse stress de supervivencia: comparar con una regla simple; definir hipótesis, métrica fuera de muestra y condición de refutación antes del experimento.

## Validación y aceptación

- Casos manuales y conciliación de totales; sensibilidad y límites de parámetros.
- Datos point-in-time y separación temporal cuando haya estimación.
- Pruebas de entradas inválidas, unidades incompatibles, faltantes y perímetro.
- Comparar resultados con fuente/anexo oficial aplicable antes de afirmar cumplimiento.
- Entregar notebook con fórmulas, gráficos de sensibilidad, resultados calculados y límites; Python como referencia y C++ solo si un benchmark justifica migración.

**Responsables objetivo:** dueño de riesgo define políticas; datos mantiene contratos; ingeniería implementa; validación independiente cuestiona métodos; cumplimiento verifica aplicabilidad; comité decide excepciones. Ninguna alerta constituye una decisión automática de cumplimiento.
