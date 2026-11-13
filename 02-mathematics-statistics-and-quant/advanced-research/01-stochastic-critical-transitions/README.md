# Stochastic Dynamical Systems & Critical Transitions

> **Madurez: S2 acotado — auditoría OU de discretización e identificación.** El programa completo de detección de transiciones no está validado. El protocolo original se conserva debajo como agenda, no como trabajo terminado.

## MVP ejecutable — 2026-10-17

¿Puede el aumento de ruido imitar la varianza de un sistema que pierde recuperación, y puede una discretización Euler fabricar señales espurias?

Se implementan transiciones gaussianas exactas Ornstein–Uhlenbeck, Euler–Maruyama y una referencia independiente por exponencial matricial de Van Loan. Se comparan momentos finitos, estabilidad, recursos y episodios estacionarios con varianzas poblacionales iguales pero distinta recuperación.

### Reproducción con un comando

Desde esta carpeta, con **Python 3.12, make, venv y acceso a PyPI**:

```bash
make run
```

Desde la raíz del repositorio:

```bash
make -C 02-mathematics-statistics-and-quant/advanced-research/01-stochastic-critical-transitions run
```

El comando crea `.venv`, instala las versiones directas fijadas, ejecuta Ruff/mypy/tests con cobertura, las 84 simulaciones y los 3.200 episodios, regenera el informe y ejecuta el notebook completo. Si `python3` no es 3.12: `make run PYTHON=python3.12`. No requiere datos privados ni descargas durante el experimento. Dependencias transitivas no bloqueadas; `benchmarks/environment.txt` registra las resueltas. Una reproducción reescribe únicamente los resultados generados de este MVP; los tiempos varían por máquina.

El notebook se ejecuta realmente con IPython en proceso, capturando stdout y salidas enriquecidas; no necesita sockets locales. La primera prueba con nbclient falló por la restricción de sockets del entorno y no se presenta como exitosa. En un entorno convencional, `.venv/bin/python scripts_notebook.py --kernel` ejecuta el mismo cuaderno con nbclient. El workflow general Notebook Reliability valida además los notebooks modificados con un kernel separado.

QA: figura PNG inspeccionada visualmente; celdas, salidas y formato del notebook validados automáticamente. No se hizo una revisión visual integral en un visor de notebooks. Para completarla, abrir `notebook.ipynb` en Jupyter; alternativamente instalar `nbconvert` y exportar con `python -m jupyter nbconvert --to html notebook.ipynb`. `benchmarks/checklist.json` registra esta distinción. La guía de notebooks influyó en la separación método/datos/resultados/límites y en conservar las salidas reales.

### Estructura y salidas

- `src/ou.py`: transiciones, simulación y diagnósticos; `src/reference.py`: oráculo; `src/benchmark.py`: experimento, figura y registros.
- `tests/`: tests unitarios, edge cases y propiedades Hypothesis. `make verify` requiere entorno ya instalado.
- `config.json`: hipótesis, umbrales, semillas, baselines y política de hardware.
- `benchmarks/discretization.csv`: 84 corridas; precisión, estabilidad, tiempo y memoria rastreada.
- `benchmarks/identification.csv`: 3.200 episodios; tasas indefinidas explícitas.
- `benchmarks/population.csv`, `oracle.csv`, `summary.csv`, `results.json`, `audit.png`, `example_paths.npz`.
- `notebook.ipynb`: cuatro celdas de código realmente ejecutadas; `informe.md`: resultados y límites.
- `referencias.bib`, `fuentes.md`: antecedentes verificados, sin reivindicar novedad algorítmica.
- `MVP.md`: contrato y exclusiones. CI específico reproduce el comando.

### Interpretación y límites

Para media cero conocida, Var(X)=σ²/(2κ) no identifica κ sin controlar σ. La correlación lag-1 exp(−κΔt) distingue **estos dos mecanismos OU especificados**, no toda fuente posible de fragilidad. No hay bifurcación, transición realizada, evaluación prospectiva de falsas alarmas, ruido coloreado ni validación financiera. El indicador estimado es un coeficiente OLS condicional con media cero conocida, no Pearson con media estimada. Ver `informe.md` para resultados medidos y cobertura exacta. Los métodos matemáticos son conocidos; el avance es un artefacto reproducible nuevo en este programa.

## Protocolo original — agenda pendiente fuera del MVP

## Pregunta de investigación

¿Pueden detectarse transiciones críticas antes de que ocurran sin confundirlas con cambios de régimen inducidos por ruido?

## Hipótesis contrastable

El método propuesto supera a baselines explícitos en al menos una métrica predefinida, sin degradación inaceptable en robustez, calibración ni costo. Esta hipótesis debe operacionalizarse antes de observar resultados.

## Formulación matemática

dX_t=f(X_t,θ_t)dt+σ(X_t,θ_t)dW_t; estabilidad por espectro del Jacobiano y tiempos de recuperación.

**Trabajo teórico pendiente:** definir espacios de probabilidad y parámetros, supuestos de existencia e identificabilidad, resultados de convergencia o estabilidad, demostraciones y contraejemplos. No se presume que tales propiedades estén establecidas.

## Modelado estadístico y estimación

Comparar autocorrelación, varianza, recuperación local y exponentes de Lyapunov contra CUSUM y change-point detection.

Estimar sesgo, varianza, consistencia bajo supuestos adecuados e intervalos de incertidumbre. Separar evaluación predictiva de identificación causal.

## Métodos numéricos y protocolo experimental

Simular saddle-node, pitchfork, ruido multiplicativo, transiciones sin bifurcación; medir anticipación, falsas alarmas y calibración.

**Diseño mínimo:** (1) generador sintético con verdad conocida; (2) baseline trivial y avanzado; (3) evaluación fuera de muestra o por réplicas independientes; (4) ablaciones y pruebas adversariales; (5) tiempos, memoria y sensibilidad a hiperparámetros; (6) semillas, versiones y resultados reproducibles.

## Aplicación económico-financiera

Fragilidad financiera y crisis de liquidez.

## Limitaciones y posibles fallos

Separar alertas de bifurcación y alertas de ruido; inferencia bajo dependencia temporal.

## Entregables y criterios de aceptación

- **S1:** revisión bibliográfica verificable, hipótesis operacionales, teoremas/proposiciones y plan preregistrado de simulación.
- **S2:** módulos `src/`, `tests/`, datos sintéticos y script de reproducción, con cobertura de invariantes y casos límite.
- **S3:** comparadores estadísticos, tablas y figuras generadas, análisis de sensibilidad, errores numéricos y benchmark de recursos.
- **S4:** réplica independiente, aplicación con datos públicos licenciados, documentación de riesgos y límites de validez.

## Estructura del programa completo prevista en S1 (solo src/tests y el MVP están implementados)

```text
theory/       # supuestos, derivaciones y pruebas
src/          # modelos, estimadores y algoritmos
tests/        # tests unitarios y estadísticos
experiments/  # simulaciones y benchmarks
data/         # manifiestos y fuentes públicas
docs/         # interpretación, limitaciones y referencias
```

**Regla de evidencia:** no reportar métricas, resultados, referencias bibliográficas ni garantías matemáticas que no hayan sido verificadas.
