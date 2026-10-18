# Nonlinear Dependence & Tail Geometry

> **Madurez: S2 acotado — auditoría de coexcedencias elípticas.** El programa completo de geometría extrema, ajuste y backtesting sigue pendiente; el protocolo original se conserva debajo como agenda.

## MVP ejecutable — 2026-10-18

¿Basta igualar Kendall tau para extrapolar colas conjuntas? Se comparan cópulas gaussiana, t4 y t30, distinguiendo L(q)=P(V>q|U>q) del límite lambda_U. Se implementan dos cuadraturas, Monte Carlo directo y condicional, una cota de varianza demostrada y tests numéricos. Son métodos conocidos: la aportación es una auditoría integrada y reproducible, no una cópula nueva.

### Instalar y reproducir con un comando

Python **3.12**, `make`, `venv` y acceso a PyPI. Desde esta carpeta:

```bash
make run
```

Desde la raíz de un checkout que contenga este MVP:

```bash
make -C 02-mathematics-statistics-and-quant/advanced-research/04-nonlinear-tail-dependence run
```

El comando crea `.venv`, instala dependencias directas fijadas, ejecuta lint/formato/tipado/tests, benchmark, informe, notebook con outputs y checklist. Si hace falta seleccionar intérprete: `make run PYTHON=python3.12`. No requiere cuentas privadas ni datos externos durante el experimento. Versiones resueltas en `benchmarks/environment.txt`; no hay lock transitivo. Reescribe los resultados generados de este MVP; los tiempos dependen del hardware.

### Estructura real

- `src/copulas.py`: modelos, tau, lambda, muestreo y estimadores.
- `src/reference.py`: integrales en dos coordenadas y segundo momento condicional.
- `src/benchmark.py`: 48 escenarios, 1.280 corridas temporizadas, memoria y figura.
- `tests/`: unitarios, propiedades Hypothesis, casos límite y ejecución del notebook.
- `config.json`: pregunta, umbrales, baselines, semillas y política de recursos.
- `benchmarks/`: CSV/JSON crudos, `audit.png`, ejemplos NPZ, logs, cobertura y checklist.
- `notebook.ipynb`: ocho celdas de código ejecutadas, problema → método → evidencia → límites.
- `informe.md`, `MVP.md`, `referencias.bib`, `fuentes.md`: interpretación, alcance y cinco antecedentes reales.

### Baselines y lectura correcta

El baseline de simulación directa usa el mismo N y los mismos parámetros que el condicional, con streams independientes y 80 réplicas por celda. Igual N no es igual tiempo: se registran ambos. El denominador N(1−q) es conocido; el cociente con denominador empírico se guarda aparte, sin convertir 0/0 en cero. Las cuadraturas comparten SciPy y no son certificados formales. La cota de varianza se aplica a parámetros conocidos y no incluye el coste de estimarlos.

La biblioteca de cartera gaussiana existente en `03-financial-risk/.../copula-gaussiana-perdidas` se conserva; aquí no se calcula capital de 200 deudores ni se modifica el contrato EL=83 de quant-libraries.

### Notebook y revisión

El notebook se ejecuta con IPython en proceso para no requerir sockets locales; captura stdout y salidas enriquecidas reales y aborta ante errores. `.venv/bin/python scripts_notebook.py --kernel` usa nbclient convencional. El workflow Notebook Reliability ejecuta el notebook modificado por separado; el workflow específico reproduce todo el MVP.

Se siguen las guías de notebooks y visualización para separar supuestos, datos, resultados e incertidumbre. Se inspecciona la figura y se validan estructura y outputs; no se afirma revisión visual integral de un visor de notebooks. Para completarla abrir `notebook.ipynb` en Jupyter o exportar con `python -m jupyter nbconvert --to html notebook.ipynb` tras instalar nbconvert.

## Protocolo S1 original — agenda fuera del alcance del MVP

## Pregunta de investigación

¿Cuándo fallan las correlaciones lineales para cuantificar pérdidas extremas conjuntas?

## Hipótesis contrastable

El método propuesto supera a baselines explícitos en al menos una métrica predefinida, sin degradación inaceptable en robustez, calibración ni costo. Esta hipótesis debe operacionalizarse antes de observar resultados.

## Formulación matemática

F(x_1,…,x_d)=C(F_1(x_1),…,F_d(x_d)); λ_U=lim_{u→1}P(U_2>u|U_1>u).

**Trabajo teórico pendiente:** definir espacios de probabilidad y parámetros, supuestos de existencia e identificabilidad, resultados de convergencia o estabilidad, demostraciones y contraejemplos. No se presume que tales propiedades estén establecidas.

## Modelado estadístico y estimación

Comparar cópulas gaussianas, t, Archimedeanas y vine; estimación semiparamétrica y EVT.

Estimar sesgo, varianza, consistencia bajo supuestos adecuados e intervalos de incertidumbre. Separar evaluación predictiva de identificación causal.

## Métodos numéricos y protocolo experimental

Generar dependencia asimétrica, regímenes, independencia asintótica; backtesting de cuantiles conjuntos y bootstrap.

**Diseño mínimo:** (1) generador sintético con verdad conocida; (2) baseline trivial y avanzado; (3) evaluación fuera de muestra o por réplicas independientes; (4) ablaciones y pruebas adversariales; (5) tiempos, memoria y sensibilidad a hiperparámetros; (6) semillas, versiones y resultados reproducibles.

## Aplicación económico-financiera

Contagio, VaR/ES agregado, estrés sistémico.

## Limitaciones y posibles fallos

Identificación y extrapolación de cola con pocas observaciones extremas.

## Entregables y criterios de aceptación

- **S1:** revisión bibliográfica verificable, hipótesis operacionales, teoremas/proposiciones y plan preregistrado de simulación.
- **S2:** módulos `src/`, `tests/`, datos sintéticos y script de reproducción, con cobertura de invariantes y casos límite.
- **S3:** comparadores estadísticos, tablas y figuras generadas, análisis de sensibilidad, errores numéricos y benchmark de recursos.
- **S4:** réplica independiente, aplicación con datos públicos licenciados, documentación de riesgos y límites de validez.

## Estructura prevista para el programa completo (el MVP anterior sí está implementado)

```text
theory/       # supuestos, derivaciones y pruebas
src/          # modelos, estimadores y algoritmos
tests/        # tests unitarios y estadísticos
experiments/  # simulaciones y benchmarks
data/         # manifiestos y fuentes públicas
docs/         # interpretación, limitaciones y referencias
```

**Regla de evidencia:** no reportar métricas, resultados, referencias bibliográficas ni garantías matemáticas que no hayan sido verificadas.
