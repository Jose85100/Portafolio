# Evaluar modelos de lenguaje con rigor: intervalos, pares, jueces automáticos y compuertas de regresión

Estadística para evaluar sistemas de IA y jueces LLM, **validada contra una verdad conocida**: cobertura exacta de intervalos, comparación pareada (McNemar exacto), efecto de diseño con muestras repetidas, corrección de jueces sesgados con **inferencia asistida por predicción (PPI)**, acuerdo entre evaluadores, sesgos de verbosidad y posición, control de comparaciones múltiples y compuertas secuenciales (SPRT).

## Hallazgos (medidos en el notebook)

- Wald cubre solo 33 % con p=0,02 y n=20; Wilson y Clopper–Pearson no.
- El diseño pareado (McNemar) necesita 640 preguntas donde el independiente necesita 897 para 80 % de potencia, y la fórmula da la potencia pedida.
- Con 30 prompts × 20 muestras el IC ingenuo cubre 56 %; el IC por grupos, 95 %.
- Un juez permisivo sobreestima la tasa de pase en +0,107; PPI y Rogan–Gladen corrigen el sesgo; PPI reduce el RMSE (0,040 vs 0,050 del oro con 100 etiquetas) y **solo ahorra etiquetas si el juez es bueno** (con 65 % de precisión empeora, con 95 % equivale a 4,5× más etiquetas).
- Con sesgo de verbosidad, el juez crudo declara «mejor» al modelo más verboso en ~100 % de los experimentos aun siendo iguales; PPI mantiene el error cerca del nominal.
- Paradoja del kappa: dos jueces con 95 % de precisión tienen κ=0,81 con prevalencia 50 % y κ=0,45 con 95 %, con el mismo acuerdo bruto.
- El sesgo de posición infla 0,5→0,73 la tasa de victoria de «A primero»; intercambiar el orden la recupera a 0,50.
- El SPRT conserva los errores con ~46–63 % menos discordantes que el diseño de tamaño fijo.

## Estructura

```text
src/        librería (módulos: `stats` (intervalos, McNemar, tamaños de muestra, κ de Cohen/Fleiss, α de Krippendorff, Rogan–Gladen, PPI, Holm, BH), `sequential` (SPRT y compuerta fija) y `world` (ítems, modelos IRT, jueces con sesgos).)
tests/      pruebas unitarias (unittest)
docs/       ARCHITECTURE.md (diagrama y decisiones de diseño)
notebook.ipynb   desarrollo completo con pruebas automáticas (assert) y lecturas calculadas desde los datos
main.py     demostración corta
```

## Cómo ejecutar

```bash
python3 main.py                                   # demostración corta
python3 -m unittest discover -s tests             # pruebas unitarias
python3 -m unittest tests.test_notebooks          # (desde la raíz del repo) ejecuta el notebook de principio a fin
```

## Datos

Simulación con semilla fija y verdad conocida; sin datos reales ni confidenciales.

## Límites

- Modelos logísticos de un parámetro; los reales tienen perfiles multidimensionales.
- Jueces con error constante o dependiente de la verbosidad; los reales varían con la tarea y la versión.
- PPI supone etiquetas humanas correctas y representativas; el SPRT, discordancias independientes.
