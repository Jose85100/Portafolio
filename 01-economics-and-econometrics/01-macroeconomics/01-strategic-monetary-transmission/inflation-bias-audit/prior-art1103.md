# Matriz de prior art — incremento de dependencia

| Fuente | Problema / supuestos | Método y evidencia | Diferencia concreta de este incremento |
|---|---|---|---|
| Kydland & Prescott (1977), `kydland1977` | Inconsistencia temporal en política; economía de compromiso | Modelo dinámico de reglas frente a discreción | Conserva la pérdida y las reglas; sólo reemplaza la entrada de varianza, sin nueva teoría monetaria |
| Barro & Gordon (1983), `barro1983positive` | Inflación sesgada con objetivo de producto natural | Modelo reputacional/estático de política monetaria | El experimento de hoy no estima inflación ni reputación; usa la fórmula previa como downstream diagnostic |
| Prais & Winsten (1954), `praiswinsten1954` | Regresión con errores serialmente correlacionados AR(1) | Transformación de GLS para AR(1) | Nuestro GLS es el baseline competitivo exacto y lineal en n; no se atribuye como novedoso |
| Penn State STAT 510, `psuar1` | Propiedades de AR(1) estacionario | Media, varianza y autocovarianza por rezago | Suministra el dominio estacionario que se impone al generador sintético |
| Isserlis (1918), `isserlis1918` | Momentos de distribuciones normales multivariadas | Fórmula de productos-momentos gaussianos | Justifica Cov(D²,D'²)=2Cov(D,D')² usada en la varianza de pares solapados |
| Cochran (1934), `cochran1934` | Distribución de formas cuadráticas normales | Caracterización de formas cuadráticas y chi-cuadrado | Apoya el pivote exacto del residual GLS blanqueado con media estimada |
| NIST/SEMATECH, `nistchisquare` | Intervalo para varianza normal iid | Inversión del pivote chi-cuadrado | Referencia al baseline iid; no es válido al ignorar AR(1) |
| Wilson (1927), `wilson1927` | Intervalo para proporciones | Límite Wilson usado para resumir cobertura simulada | Sólo cuantifica incertidumbre Monte Carlo de coberturas, no cambia el teorema |

Fuentes de fundamentos comprobadas el 2026-11-03: Penn State STAT 510, Cowles/Yale, Oxford Academic, Cambridge Core y NIST. El material de Prais–Winsten es un discussion paper y la página de GLS es un texto docente secundario; el núcleo teórico se atribuye a las fuentes primarias de Isserlis y Cochran. Cobertura: suficiente para el estimador de momentos gaussianos y el baseline GLS bajo AR(1) conocido; incompleta para \(\rho\) desconocido, bootstrap/HAC, procesos no gaussianos y validación macroeconómica empírica.
