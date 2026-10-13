# credit portfolio steering leadership

**Rol objetivo:** Head of Credit Risk. **Estado:** S1: diseño de investigación e ingeniería, no motor ejecutable.

## Decisión y alcance
Asignar límites, originación y cobranza por cohortes y segmentos. Caso: MCA y crédito digital.

## Modelo matemático
max sum_s (ingreso_s - EL_s - fondeo_s - opex_s) x_s sujeto a EAD, concentración y presupuesto. Formalizar índices, unidades, horizonte, restricciones duras y política alternativa; comprobar existencia de solución y sensibilidad a no convexidad.

## Inferencia y riesgo de modelo
Transiciones Markov por vintage, EAD/PD/LGD, intervalos bootstrap y drift; evitar usar información posterior al corte. Separar estimación predictiva de afirmaciones causales, cuantificar incertidumbre y comparar contra una política simple.

## Métodos numéricos
Optimización restringida + simulación mensual de cosechas. Implementar una versión baseline determinista antes de algoritmos complejos; documentar convergencia, costo computacional, estabilidad y casos límite.

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
