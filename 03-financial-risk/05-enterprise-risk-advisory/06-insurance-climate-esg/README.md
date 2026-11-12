# Seguros, clima y conducta — bases + 7 proyectos

**Bases especializadas:** [fundamentals/](fundamentals/) · **Bases transversales:** [00-foundations/](../00-foundations/)

Los fundamentos son independientes del catálogo; **no cuentan** entre los siete proyectos.

Se mantienen los tres proyectos existentes y se incorporan cuatro líneas nuevas. Todos deben adoptar los [contratos y criterios transversales](../00-architecture/README.md) sin sustituir su matemática especializada.

## Catálogo

- **Existente:** [Pricing y reservas actuariales](insurance-reserving/)
- **Existente:** [Riesgo climático físico y transición](climate-risk/)
- **Existente:** [Conducta y protección del consumidor](conduct-risk/)
- **Nuevo S1:** [Transmisión de riesgo climático al crédito](climate-hazard-credit/)
- **Nuevo S1:** [Incertidumbre de reservas actuariales](actuarial-reserve-uncertainty/)
- **Nuevo S1:** [Alertas tempranas de daño al consumidor](conduct-harm-early-warning/)
- **Nuevo S1:** [Dependencia espacial de pérdidas climáticas](climate-insurance-dependence/)

## Cobertura de aplicaciones y datos pendientes

| Tema | Evidencia disponible y alcance |
|---|---|
| [Riesgo climático](climate-risk/) | Registros agregados UNGRD; las filas no necesariamente son eventos únicos. |
| [Amenaza climática y crédito](climate-hazard-credit/) | Señal de precipitación NASA POWER para ciudades; no estima pérdida o default. |
| [Reservas actuariales](insurance-reserving/) | Triángulo observado de pagos CAS/NAIC con corte histórico de 2007 y evaluación posterior a edad 10. |
| [Incertidumbre de reservas](actuarial-reserve-uncertainty/) | Sensibilidad y bootstrap condicional de factores para el mismo triángulo; no intervalo de predicción ni incertidumbre total. |
| [Dependencia clima-seguro](climate-insurance-dependence/) | **Pendiente:** siniestros asegurados fechados y georreferenciados, exposición y amenaza comparables; lluvia aislada no identifica dependencia de pérdidas. |
| [Alerta de daño de conducta](conduct-harm-early-warning/) | **Pendiente:** quejas y daños trazables por fecha, población expuesta y resolución; no inferir tasas de daño a partir de quejas sin denominador. |
| [Riesgo de conducta](conduct-risk/) | **Pendiente:** incidentes y controles de conducta, exposición y resultados; quejas agregadas por sí solas no prueban incumplimiento o daño. |

Los casos CAS usan un solo grupo y un corte histórico; la fuente CAS/S&P exige atribución y los resultados no demuestran suficiencia de reservas vigentes.
