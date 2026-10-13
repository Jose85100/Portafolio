# cfo capital liquidity and funding

**Rol objetivo:** CFO. **Estado:** S1: diseño de investigación e ingeniería, no motor ejecutable.

## Decisión y alcance
Determinar fondeo, dividendos, crecimiento y capital multianual. Caso: Fintech de lending y pagos.

## Modelo matemático
max sum_t beta^t FCF_t sujeto a identidad de balance, caja minima, covenants y capital. Formalizar índices, unidades, horizonte, restricciones duras y política alternativa; comprobar existencia de solución y sensibilidad a no convexidad.

## Inferencia y riesgo de modelo
Forecast por escenarios, curvas de fondeo, sensibilidad de mora/prepago, reconciliación contable. Separar estimación predictiva de afirmaciones causales, cuantificar incertidumbre y comparar contra una política simple.

## Métodos numéricos
Simulación stock-flow consistent + programación estocástica. Implementar una versión baseline determinista antes de algoritmos complejos; documentar convergencia, costo computacional, estabilidad y casos límite.

## Arquitectura
Datos versionados → validación y calidad → estimación → escenarios → optimizador → explicación de trade-offs → aprobación humana → monitoreo. Interfaces con contratos explícitos y auditoría de parámetros.

## Paquete de entrega S2
- `src/`: motor con interfaces tipadas y validación de entradas.
- `tests/`: invariantes, escenarios límite, reproducibilidad y regresión.
- `examples/`: caso sintético con verdad conocida, baseline y alternativas.
- `docs/`: teoría, calibración, seguridad, gobernanza, análisis de sensibilidad y nota para comité.
- CI reproducible; no declarar S2 hasta verificar ejecución.

## Criterios de decisión ejecutiva
Registrar responsable, capital o presupuesto comprometido, pérdidas adversas, trigger de revisión, riesgos residuales, evidencia disponible y supuestos que invalidarían la recomendación.
