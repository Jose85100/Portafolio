# Auditoría de permutación condicional para Christoffersen

MVP reproducible que mide tamaño y potencia finitos del test de independencia de excepciones VaR. Compara el
baseline `LR_ind ~ chi²(1)` con dos calibraciones que condicionan en el número observado de excepciones:

1. p-valor de permutación no aleatorizado, válido pero conservador ante empates;
2. p-valor de permutación aleatorizado, que rompe empates con una semilla registrada.

No se afirma que la permutación o los tests aleatorizados sean nuevos. La contribución incremental al portafolio
es convertir el conservadurismo ya observado en `backtesting-var-kupiec-christoffersen/notebook.ipynb` en una
auditoría modular, testeada y falsable.

## Reproducción en un comando

Requiere Python 3.12 y crea un entorno local aislado:

```bash
./run.sh
```

Salida verificable en `results/`: `summary.csv`, `trials.csv`, `run.json`, `calibration.png`, cobertura, lint,
tipos y tests. El comando reconstruye y ejecuta `notebook.ipynb` de arriba abajo. Alternativa Docker:

```bash
docker build -t christoffersen-audit . && docker run --rm christoffersen-audit
```

## Hipótesis falsable

Con 250 observaciones, probabilidad de excepción 1%, nivel 5% y hits IID, el test asintótico rechazará menos de
3%; la permutación no aleatorizada no corregirá materialmente ese conservadurismo, mientras la versión
aleatorizada quedará a menos de 2 puntos porcentuales del 5%. Bajo una cadena Markov con la misma tasa
estacionaria y `P(hit_t=1 | hit_t-1=1)=35%`, se reporta potencia sin imponer un umbral favorable a priori.

## Diseño

- DGP nulo: Bernoulli IID(1%).
- DGP alternativo: Markov estacionario con tasa marginal objetivo 1% y persistencia 35%.
- 2.000 trials, 1.999 permutaciones por conteo de excepciones, semilla `20261021`.
- Baseline: p-valor asintótico chi-cuadrado de Christoffersen.
- Candidatos: p-valor condicional conservador y p-valor aleatorizado ante empates.
- Métricas: frecuencia de rechazo (tamaño bajo nula, potencia bajo alternativa), tiempo y memoria indirecta por
  tamaño de artefactos. La tasa estacionaria observada se informa para controlar comparabilidad.

## Estructura

- `src/backtest.py`: estadístico y calibraciones.
- `src/experiment.py`: DGP y benchmark.
- `src/main.py`: CLI, CSV, JSON y figura.
- `tests/`: unitarios, property-based y edge cases.
- `benchmarks/config.json`: configuración inmutable del experimento.
- `notebook.ipynb`: narrativa ejecutada con outputs visibles.
- `informe.md`: interpretación crítica, ablations y límites.

## Uso responsable

El experimento es sintético. Condicionar en el conteo prueba independencia, no cobertura incondicional. El test
aleatorizado es válido en frecuencia pero una decisión individual marginal depende del RNG; el artefacto conserva
la semilla para auditoría. No sustituye validación independiente, backtesting regulatorio ni gobierno de modelo.

## Aplicación institucional pendiente: datos mínimos y brecha pública

La auditoría mide tamaño y potencia del test bajo DGP controlados; no calcula excepciones de una cartera real. En la revisión del inventario público SFC del 11 de noviembre de 2026 se encontró la [página de reportes SFC](https://www.superfinanciera.gov.co/publicaciones/19161/industrias-supervisadasinteres-del-vigiladoreportes-19161/), que ofrece matrices de volatilidad para el reporte oficial de riesgo de mercado y validadores de VaR regulatorio e informativo. Estos artefactos describen insumos y reglas de transmisión, pero no proporcionan una serie pública de pronósticos VaR diarios emparejados con P&L realizado por portafolio. La [FAQ de mercado público de valores de la SFC](https://www.superfinanciera.gov.co/preguntas-frecuentes/25/25-mercado-publico-de-valores/) remite la información disponible sobre composición de portafolios al sector pensional; no encontré en el inventario local/Drive un panel comparable de VaR y P&L para una cartera institucional.

Las series oficiales de tasas usadas en los companions de mercado permiten calcular shocks de factores y P&L por duración asumida. No contienen posiciones de una entidad, pronósticos de su modelo, P&L contable/valorado ni sus convenciones operativas; reutilizarlas como si fueran excepciones institucionales sería una validación falsa. Por esa incompatibilidad de grano no se construye aquí un backtest observado ni se atribuye evidencia real a la calibración por permutación.

Para una aplicación de cartera, el extracto mínimo autorizado debe tener una fila por `portfolio_id × fecha de pronóstico × modelo/version`, con: VaR numérico, nivel de confianza, horizonte, moneda/unidad y convención de pérdidas; P&L realizado del horizonte siguiente bajo la valoración oficial; indicador de excepción recalculable desde ambos campos; fecha de información disponible, calendario y banderas de faltantes/revisiones. Debe preservar una ventana fuera de tiempo continua, la misma definición de cartera y horizonte, y suficientes observaciones para evaluar tamaño/potencia en niveles de cola raros. Si las posiciones varían, se requiere el identificador/versionado de cartera y los flujos que expliquen cambios de composición. El dueño del modelo debe aprobar la definición de P&L, nivel/horizonte y tratamiento de días faltantes antes del cálculo.

Con ese panel se podría comparar la decisión asintótica de Christoffersen con la permutación condicional sobre la secuencia real de excepciones, reportando tamaño/potencia solo cuando exista diseño de referencia adecuado; una sola secuencia institucional no identifica por sí misma el tamaño frecuentista. Hasta entonces, las cifras de este repositorio siguen siendo propiedades de las simulaciones configuradas arriba, no desempeño de una cartera, entidad o modelo autorizado.
