# Fundamentos de matemáticas y estadística

**40 lecciones en ocho categorías, ocho notebooks y 18 figuras.** Ruta de estudio para comprender las herramientas matemáticas del portafolio. Los ejemplos son analíticos o sintéticos; no representan desempeño real ni datos de clientes.

El curso parte de álgebra elemental y avanza hacia proyecciones, inferencia, optimización y dinámica. Cada categoría tiene su propio índice. Las lecciones nuevas 25–40 desarrollan demostraciones, cálculos completos y ejercicios con solución. Los teoremas usados sin demostración general se identifican como tales.

## Categorías

| Categoría | Lecciones | Contenido |
|---|---:|---|
| [Fundamentos y demostraciones](01-fundamentos/) | 3 | Números, conjuntos, lógica y validez de los argumentos. |
| [Álgebra](02-algebra/) | 4 | Ecuaciones, desigualdades, polinomios y números complejos. |
| [Funciones y trigonometría](03-funciones-y-trigonometria/) | 3 | Gráficas, ondas, crecimiento y transformación logística. |
| [Álgebra lineal](04-algebra-lineal/) | 4 | Matrices, rango, bases, autovalores y QR. |
| [Cálculo y optimización](05-calculo-y-optimizacion/) | 9 | Límites, derivadas, integrales, Taylor, convexidad y algoritmos. |
| [Probabilidad](06-probabilidad/) | 7 | Modelos discretos y continuos, dependencia y Bayes. |
| [Estadística e inferencia](07-estadistica/) | 7 | Estimación, regresión, incertidumbre, contrastes y bootstrap. |
| [Sistemas dinámicos](08-sistemas-dinamicos/) | 3 | Recurrencias, ecuaciones diferenciales y cadenas de Markov. |

## Orden de estudio sugerido

1. **Fundamentos y álgebra:** lenguaje de conjuntos, números, fracciones, desigualdades y métodos de demostración.
2. **Funciones:** composición, inversas, trigonometría, exponencial y logística. Los complejos requieren también trigonometría.
3. **Álgebra lineal:** vectores, sistemas, bases, rango y formas cuadráticas.
4. **Cálculo:** límites, derivadas, reglas de derivación e integración; después, series, cálculo multivariable y convexidad.
5. **Probabilidad:** conteo, variables discretas, densidades, conjuntas, momentos y condicionales.
6. **Estadística:** muestreo, verosimilitud, regresión, contrastes, potencia, multiplicidad y remuestreo. QR conecta regresión con álgebra lineal.
7. **Métodos y dinámica:** bisección, Newton, gradiente, recurrencias, ecuaciones diferenciales y Markov.

Este orden no exige terminar toda una categoría antes de abrir otra. Consulta los prerrequisitos al comienzo de cada archivo. Los números de las lecciones conservan su identidad histórica, no representan un único orden obligatorio.

## Nuevos desarrollos: lecciones 25–40

| Lección | Desarrollo principal |
|---|---|
| [25. Números reales, intervalos y completitud](01-fundamentos/25-numeros-reales-y-completitud.md) | Objetivo: distinguir racionales, reales, cotas y supremos. Antes: lecciones 1, 8 y 14. |
| [26. Cómo construir y revisar una demostración](01-fundamentos/26-metodos-de-demostracion.md) | Objetivo: practicar implicación, contraposición, contradicción e inducción. Antes: lección 8. |
| [27. Polinomios: raíces, factorización y multiplicidad](02-algebra/27-polinomios-raices-y-factorizacion.md) | Objetivo: deducir herramientas de resolución y reconocer cuándo una transformación añade soluciones. Antes: lecciones 1, 2 y 14. |
| [28. Números complejos: álgebra y rotaciones](02-algebra/28-numeros-complejos.md) | Objetivo: operar con complejos y conectar forma cartesiana, polar y oscilaciones. Antes: álgebra y trigonometría. |
| [29. Exponencial, logaritmo y función logística](03-funciones-y-trigonometria/29-exponencial-logaritmo-y-logistica.md) | Objetivo: derivar crecimiento continuo, duplicación y transformación logística. Antes: funciones, logaritmos y derivadas. |
| [30. Espacios vectoriales, bases y rango](04-algebra-lineal/30-espacios-bases-y-rango.md) | Objetivo: construir bases, interpretar rango y relacionar soluciones con grados de libertad. Antes: vectores y sistemas lineales. |
| [31. Autovalores, formas cuadráticas y matrices de covarianzas](04-algebra-lineal/31-autovalores-y-formas-cuadraticas.md) | Objetivo: calcular autovalores sencillos y entender positividad. Antes: matrices, determinantes y bases. |
| [32. Límites y continuidad: definiciones y garantías](05-calculo-y-optimizacion/32-limites-continuidad-y-teoremas.md) | Objetivo: usar ε–δ y distinguir existencia de una raíz, de un extremo y de una derivada. Antes: desigualdades y funciones. |
| [33. Buscar raíces y minimizar: tres algoritmos distintos](05-calculo-y-optimizacion/33-raices-y-descenso-de-gradiente.md) | Objetivo: derivar bisección, Newton y descenso de gradiente, con criterios de parada. Antes: límites, derivadas y convexidad. |
| [34. Binomial, Poisson y geométrica: elegir el experimento](06-probabilidad/34-binomial-poisson-y-geometrica.md) | Objetivo: derivar tres distribuciones discretas y separar sus supuestos. Antes: combinatoria y esperanza. |
| [35. Distribuciones conjuntas y transformaciones](06-probabilidad/35-distribuciones-conjuntas-y-transformaciones.md) | Objetivo: integrar una densidad conjunta y justificar cambios de variable. Antes: integración, momentos y probabilidad condicional. |
| [36. Contrastes: errores, potencia y comparaciones múltiples](07-estadistica/36-contrastes-potencia-y-multiplicidad.md) | Objetivo: construir un contraste sencillo y derivar su potencia. Antes: muestreo, normal y estadística básica. |
| [37. Bootstrap y método delta: incertidumbre de estadísticas transformadas](07-estadistica/37-bootstrap-y-metodo-delta.md) | Objetivo: derivar una aproximación analítica y entender qué reproduce el remuestreo. Antes: Taylor, inferencia y varianza. |
| [38. Ecuaciones diferenciales: evolución, equilibrio y discretización](08-sistemas-dinamicos/38-ecuaciones-diferenciales.md) | Objetivo: resolver modelos lineales y logísticos e interpretar Euler. Antes: derivadas, integración y recurrencias. |
| [39. Cadenas de Markov: transición y distribución estacionaria](08-sistemas-dinamicos/39-cadenas-de-markov.md) | Objetivo: construir una matriz estocástica, hallar un equilibrio probabilístico y distinguirlo de convergencia. Antes: probabilidad y matrices. |
| [40. Ortogonalidad y QR: resolver sin formar una inversa](04-algebra-lineal/40-ortogonalidad-y-factorizacion-qr.md) | Objetivo: derivar Gram–Schmidt y resolver mínimos cuadrados mediante QR. Antes: bases, producto interno y mínimos cuadrados. |

## Estudiar con profundidad

En cada sesión:

1. Escribe el dominio, la unidad y los supuestos.
2. Justifica cada transformación; distingue equivalencia de implicación.
3. Reproduce el ejemplo antes de consultar la solución.
4. Busca un contraejemplo cuando se retira una hipótesis.
5. Explica el resultado con palabras y comprueba su escala.

Un ejemplo numérico ilustra; una demostración justifica una afirmación general bajo sus hipótesis. Una prueba automatizada complementa ambas, pero no las sustituye.

### Notación esencial

$x$ es una variable; $f(x)$ es un valor de función. $\sum_{i=1}^n x_i$ suma observaciones. $\mathbb R$ son los reales; $\in$ significa pertenencia. $\Rightarrow$ indica implicación y $\Leftrightarrow$ equivalencia. Para probabilidad, $E[X]$ es esperanza y $\operatorname{Var}(X)$ varianza cuando existen. Revisa siempre si una tasa está en fracción o porcentaje y a qué periodo corresponde.

## Notebooks

Cada notebook está dentro de su categoría, en `notebooks/`. Contiene explicación, código, figuras, ejercicios, soluciones y comprobaciones.

| Categoría | Notebook |
|---|---|
| Funciones y trigonometría | [01 algebra y funciones](03-funciones-y-trigonometria/notebooks/01-algebra-y-funciones.ipynb) |
| Álgebra lineal | [02 vectores y sistemas](04-algebra-lineal/notebooks/02-vectores-y-sistemas.ipynb) |
| Cálculo y optimización | [03 derivadas y optimizacion](05-calculo-y-optimizacion/notebooks/03-derivadas-y-optimizacion.ipynb) |
| Cálculo y optimización | [04 integracion y convergencia](05-calculo-y-optimizacion/notebooks/04-integracion-y-convergencia.ipynb) |
| Probabilidad | [05 bayes y distribuciones](06-probabilidad/notebooks/05-bayes-y-distribuciones.ipynb) |
| Estadística e inferencia | [06 muestreo e inferencia](07-estadistica/notebooks/06-muestreo-e-inferencia.ipynb) |
| Estadística e inferencia | [07 regresion y residuos](07-estadistica/notebooks/07-regresion-y-residuos.ipynb) |
| Sistemas dinámicos | [08 series taylor y dinamica](08-sistemas-dinamicos/notebooks/08-series-taylor-y-dinamica.ipynb) |

Desde la raíz del repositorio:

```bash
python3 -m pip install -r 02-mathematics-statistics-and-quant/basic/requirements-notebooks.txt
python3 02-mathematics-statistics-and-quant/basic/ejecutar_notebooks.py
```

El ejecutor encuentra los notebooks de forma recursiva y usa un kernel limpio por archivo. También los detecta el sistema existente de `tests/test_notebooks.py`.

**Evidencia original de los ocho notebooks:** se ejecutaron 118 celdas, con salidas guardadas y 18 figuras revisadas. El entorno bloqueó sockets TCP e IPC de Jupyter, por lo que la ejecución se realizó en proceso, con un espacio Python limpio por notebook y captura de stdout y figuras Agg. La ejecución mediante kernel no se verificó aquí. El [manifiesto](VALIDACION.json) conserva método, versiones y rutas; las lecciones 25–40 no añaden nuevos notebooks ni modifican sus resultados.

## Comprobaciones matemáticas

Los verificadores solo requieren la biblioteca estándar de Python:

```bash
python3 02-mathematics-statistics-and-quant/basic/verificar_ejemplos.py
python3 02-mathematics-statistics-and-quant/basic/verificar_desarrollos.py
python3 02-mathematics-statistics-and-quant/basic/verificar_ampliacion.py
```

El último comprueba referencias de las lecciones 25–40: factorizaciones, raíces complejas, rango, autovectores, bisección, momentos discretos, potencia, bootstrap exacto, ecuaciones diferenciales, Markov y QR. Usa fracciones exactas cuando corresponde y tolerancias explícitas para cálculos aproximados. Las comprobaciones se limitan a sus ejemplos; no validan aplicaciones reales.

## Conexión con el portafolio

Continúa con [quant-libraries](../quant-libraries/) para contratos numéricos y con [quantitative-methods](../quantitative-methods/) para métodos aplicados. El material de investigación avanzada requiere más formación en análisis, procesos estocásticos y optimización.

## Lecturas para profundizar

Referencias bibliográficas, sin reproducir sus textos: OpenStax, *Algebra and Trigonometry 2e* y *Calculus*, volúmenes 1–3; Strang, *Introduction to Linear Algebra*, 6.ª edición; Blitzstein y Hwang, *Introduction to Probability*, 2.ª edición; OpenStax, *Introductory Statistics 2e*. Estas notas son material introductorio propio y no equivalen a completar esos libros.
