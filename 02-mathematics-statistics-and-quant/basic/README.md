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
