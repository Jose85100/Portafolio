# Brecha de datos: capital económico corporativo

**Corte de revisión:** 2026-11-11. **Estado:** existe contexto agregado oficial SFC de solvencia y deterioro contable; no existe una distribución institucional de pérdidas ni dependencia entre riesgos para estimar capital económico.

El companion [observado SFC](observed-sfc-capital-loss-context/README.md) agrega solvencia regulatoria por entidad y la relaciona descriptivamente con deterioro contable neto acumulado de los establecimientos de crédito sin IOEs. Sirve como contexto sectorial y para probar reproducibilidad del flujo de datos. El deterioro contable agregado no es una muestra de pérdidas económicas evento a evento; los ratios de solvencia son relaciones regulatorias de capital sobre activos ponderados, no medidas de VaR.

Una agregación VaR/ES necesita pérdidas comparables y exposición por unidad de riesgo, no solamente indicadores de mercado, balances agregados, solvencia o escenarios sintéticos. Sin frecuencia, severidad, dependencia, cambios de perímetro y acciones de mitigación observadas, el capital agregado no es identificable en este portafolio. El proxy contable SFC no valida la pérdida esperada/inesperada institucional ni autoriza escalar el capital regulatorio de un tercero a una empresa.

## Datos mínimos

- Taxonomía institucional de riesgos y registro de eventos con fecha, causa, pérdida bruta/neta, recuperación y exposición.
- Series por unidad de negocio/producto, denominadores, cambios de perímetro y trazabilidad contable.
- Factores comunes, dependencias condicionadas, controles y mitigaciones con evidencia de resultado.
- Horizonte/confianza aprobados, tratamiento de riesgo extremo, datos externos autorizados y permisos.

Validación requiere conciliación con pérdidas financieras y reportes regulatorios aplicables, cobertura de colas, backtesting donde proceda, pruebas de sensibilidad/dependencia, escenarios de estrés y asignación estable del capital. Los proxies públicos actuales contextualizan solvencia y deterioro contable del sector; no estiman capital económico de una empresa.
