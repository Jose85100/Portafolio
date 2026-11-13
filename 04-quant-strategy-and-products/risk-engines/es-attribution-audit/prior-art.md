# Revisión de historia y prior art

Base evaluada: `origin/main` en `4684267`. Se leyeron los motores de `risk-engines`, `IDEAS.md`, la API `quant::tail`, Stage 3 cashflow audit, weighted-tail audit y los paquetes de 03-financial-risk sobre VaR/ES, validación de mercado y proxies SFC/BanRep. Los PR #151–155 ya están en la base; #157 se reportó checkpoint sin código. No se encontró en estos árboles una API que distribuya ES de cartera a pérdidas aditivas por factor con masa fraccionaria y prueba de reconciliación. La conclusión es local a esta revisión, no una afirmación mundial de novedad.

| Idea comparada | Encaje/base disponible | Riesgo de duplicación / dependencia | Decisión |
|---|---|---|---|
| Motor de escenarios correlacionados multiactivo | `risk-engines` genera escenarios normales; TRM BanRep puede ser proxy observable para COP/USD | Repite simulación/escenarios y sería tentador calibrar de forma espuria a TRM solamente | Rechazada |
| ES condicionado FHS/GARCH/EVT | Investigación 03 ya cubre GARCH, FHS, EVT, backtesting | Alta duplicación; requiere historia limpia y decisiones de umbral | Rechazada |
| Atribución Euler exacta de ES finito ponderado | `weighted_tail_audit` resuelve ES agregado pero no componente atribuible | Brecha directa en uso de decisiones; puede probarse sin Drive ni pretender calibración | Elegida |

La fuente SFC vigente es la Circular Básica Financiera CE 004/2026 y su índice; el marco SARM colombiano contempla identificación, medición y metodologías estándar o internas con condiciones/no objeción aplicables. El modelo aquí no los implementa. Basilea MAR33 especifica ES 97.5% y ajuste por horizontes de liquidez para el enfoque interno de capital. Esa regla acota el contexto, pero no convierte una ES de escenarios de juguete en capital regulatorio. La definición de TRM de BanRep/SFC respalda su empleo como referencia histórica COP/USD en un trabajo empírico futuro. Este MVP no descargó ni utilizó esa serie: todos los datos son sintéticos.

## Novedad acotada y falsación

La contribución es de integración y control: contribuciones componentes coherentes con la cola del portafolio, pesos fraccionarios en el átomo VaR y reconciliación numérica de suma de contribuciones a ES, además de baselines explícitos. Está basada en resultados conocidos de ES coherente y asignación Euler; no es una nueva medida de riesgo. Se falsaría si (i) falla frente a expansión de pesos enteros, (ii) suma distinta de ES más allá de tolerancia numérica, o (iii) el baseline asigna idénticamente en configuraciones deliberadamente heterogéneas. Los resultados y pruebas están en `results/`.
