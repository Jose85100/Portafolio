# Fundamentos de matemáticas y estadística

Una ruta desde el álgebra elemental hasta la inferencia, para entender las herramientas del resto del portafolio. No exige cálculo previo; sí operar con fracciones y dedicar tiempo a resolver en papel.

## Ruta de aprendizaje

| Orden | Módulo | Pregunta central |
|---|---|---|
| 1 | [Álgebra y lenguaje matemático](01-algebra.md) | ¿Cómo transformar una expresión sin cambiar su significado? |
| 2 | [Funciones y geometría](02-funciones.md) | ¿Cómo representar una relación entre variables? |
| 3 | [Álgebra lineal](03-algebra-lineal.md) | ¿Cómo trabajar con varias ecuaciones y exposiciones? |
| 4 | [Cálculo diferencial](04-calculo-diferencial.md) | ¿Cómo medir cambios y encontrar extremos? |
| 5 | [Cálculo integral](05-calculo-integral.md) | ¿Cómo acumular cantidades que varían? |
| 6 | [Probabilidad](06-probabilidad.md) | ¿Cómo razonar bajo incertidumbre? |
| 7 | [Estadística e inferencia](07-estadistica.md) | ¿Qué permiten concluir los datos y con qué límites? |

Lee en orden. Para cada módulo: explica la intuición con tus palabras, reproduce el ejemplo sin mirar, resuelve los ejercicios y contrasta el resultado con la solución. Una respuesta numérica sin unidades ni interpretación queda incompleta.

## Convenciones

$x$ es una variable; $a$ puede ser un parámetro fijo; $f(x)$ es el valor de una función, no una multiplicación. $\sum_{i=1}^n x_i$ suma las observaciones. $\mathbb{R}$ son los reales y $\in$ significa «pertenece». $\Rightarrow$ indica implicación; $\Leftrightarrow$, equivalencia. Un ejemplo ilustra; una demostración justifica para todos los casos bajo sus supuestos.

## Verificación computacional

[verificar_ejemplos.py](verificar_ejemplos.py) reproduce cálculos de los siete módulos con la biblioteca estándar de Python:

```bash
python3 02-mathematics-statistics-and-quant/basic/verificar_ejemplos.py
```

Los controles verifican ejemplos concretos, no sustituyen demostraciones. No requiere paquetes ni acceso a datos externos. Los casos económicos son didácticos.

## Cómo conecta con el portafolio

Álgebra lineal y cálculo preparan para optimización de portafolios; probabilidad y estadística, para pérdida esperada, estimación y validación. Después continúa con [quant-libraries](../quant-libraries/) y [quantitative-methods](../quantitative-methods/). La investigación avanzada requiere más análisis, optimización y procesos estocásticos.

## Lecturas para profundizar

Referencias bibliográficas, sin reproducir sus textos: OpenStax, *Algebra and Trigonometry 2e* y *Calculus*, volúmenes 1–3; Strang, *Introduction to Linear Algebra*, 6.ª edición; Blitzstein y Hwang, *Introduction to Probability*, 2.ª edición; OpenStax, *Introductory Statistics 2e*. Estas notas son una introducción propia, no un curso completo equivalente a esos libros.

## Segunda etapa: ampliar el razonamiento

Después de los siete módulos iniciales:

| Lección | Tema | Prerrequisito |
|---|---|---|
| 8 | [Conjuntos, lógica y demostraciones](08-conjuntos-logica-y-demostraciones.md) | Álgebra |
| 9 | [Combinatoria](09-combinatoria.md) | Álgebra y probabilidad inicial |
| 10 | [Sucesiones, series y Taylor](10-sucesiones-series-y-taylor.md) | Funciones y derivadas |
| 11 | [Cálculo multivariable y restricciones](11-calculo-multivariable-y-restricciones.md) | Álgebra lineal y derivadas |
| 12 | [Estadística robusta y diagnóstico](12-estadistica-robusta-y-diagnostico.md) | Estadística descriptiva |
| 13 | [Ecuaciones en diferencias](13-ecuaciones-en-diferencias.md) | Sucesiones |

## Laboratorio en notebooks

Los ocho notebooks guardan explicaciones, código editable, resultados, **18 figuras**, ejercicios con soluciones y comprobaciones. Contienen 118 celdas en total. Están pensados como tutoriales iniciales: anticipa el resultado, ejecuta y explica lo que observas.

| Notebook | Experimento y pregunta |
|---|---|
| [01 · Álgebra y funciones](notebooks/01-algebra-y-funciones.ipynb) | Crecimiento compuesto, logaritmos y raíces: ¿qué cambia al transformar una función? |
| [02 · Vectores y sistemas](notebooks/02-vectores-y-sistemas.ipynb) | Sistemas casi singulares: ¿un residuo pequeño garantiza estabilidad? |
| [03 · Derivadas y optimización](notebooks/03-derivadas-y-optimizacion.ipynb) | Diferencias finitas y restricciones: ¿un paso menor siempre mejora la derivada? |
| [04 · Integración y convergencia](notebooks/04-integracion-y-convergencia.ipynb) | Trapecios y área con signo: ¿cómo medir el error? |
| [05 · Bayes y distribuciones](notebooks/05-bayes-y-distribuciones.ipynb) | Tasas base y binomial: ¿qué significa una alerta? |
| [06 · Muestreo e inferencia](notebooks/06-muestreo-e-inferencia.ipynb) | Simulación de intervalos t: ¿qué quiere decir cobertura del 95%? |
| [07 · Regresión y residuos](notebooks/07-regresion-y-residuos.ipynb) | Mínimos cuadrados y un dato extremo: ¿cuánto puede cambiar la pendiente? |
| [08 · Series, Taylor y dinámica](notebooks/08-series-taylor-y-dinamica.ipynb) | Aproximaciones y recurrencias: ¿tener equilibrio implica converger? |

### Reproducir los notebooks

Desde la raíz del repositorio:

```bash
python3 -m pip install -r 02-mathematics-statistics-and-quant/basic/requirements-notebooks.txt
python3 02-mathematics-statistics-and-quant/basic/ejecutar_notebooks.py
```

El ejecutor usa un kernel limpio por notebook, guarda resultados después de una ejecución satisfactoria y falla ante errores o assertions. También son compatibles con el descubrimiento existente de `tests/test_notebooks.py`.

**Evidencia de esta entrega (25 de octubre de 2026):** las celdas se ejecutaron en orden en un espacio Python limpio por notebook, con semillas fijas y sin errores. El entorno bloqueó los sockets TCP e IPC del kernel, por lo que esta ejecución se hizo en proceso con captura de stdout y figuras Agg, en lugar de un kernel Jupyter. Se revisaron visualmente las 18 figuras. El [manifiesto](VALIDACION.json) registra método, versiones y conteos. La ejecución mediante kernel queda disponible con el comando anterior, pero no fue verificada aquí.

### Plan sugerido

1. Sesiones 1–2: álgebra y funciones, notebook 01.
2. Sesiones 3–4: álgebra lineal y cálculo diferencial, notebooks 02–03.
3. Sesión 5: integración, notebook 04.
4. Sesiones 6–7: combinatoria, probabilidad y estadística, notebooks 05–06.
5. Sesión 8: diagnóstico robusto y regresión, notebook 07.
6. Sesiones 9–10: series, cálculo multivariable y recurrencias, notebook 08.

En cada sesión conserva tres cosas: una derivación en papel, una figura interpretada y una explicación de cuándo deja de ser válido el método.

