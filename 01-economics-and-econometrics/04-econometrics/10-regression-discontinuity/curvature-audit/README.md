# Sharp RD: curvatura, bandwidth e identificación

Nuevo componente de econometría, distinto a las auditorías IV23/24. Implementa un estimador local lineal con pendientes separadas y kernel uniforme; compara el mismo modelo con cuatro anchos de ventana. La novedad incremental es una auditoría pareada con sesgo poblacional conocido y contraejemplo donde reducir bandwidth **empeora** recuperación del efecto verdadero porque falla continuidad.

**S2 local según RESEARCH_STANDARDS.md.** No eleva la madurez de la carpeta/programa y no certifica causalidad empírica.

## Reproducir

Desde esta carpeta, Python3.11+, venv y acceso a PyPI:

```bash
bash run.sh
```

Instala dependencias directas fijadas, corre tests/coverage, ruff/mypy,18.000 estimaciones sintéticas, benchmarks y notebook narrativo ejecutado. No datos externos ni credenciales. Notebook se ejecuta secuencialmente en IPython limpio en proceso, sin kernel/socket; errores abortan y outputs permanecen guardados.

## Resultado ejecutado

Efecto causal verdadero1, n1200,1500replicas por escenario. Baselineglobal h1 tiene la misma forma lineal por lado que el método local; cambia únicamente la ventana.

| Escenario | RMSE h1 global | RMSE h0,2 local | RMSE h0,08 |
|---|---:|---:|---:|
| Curvatura simétrica |0,04688|0,07751|0,12808|
| Curvatura asimétrica, continuidad válida |0,67192|0,08295|0,12844|
| Continuidad violada |0,09525|0,57595|0,60179|

Local h0,2 reduce RMSE87,65% bajo curvatura asimétrica válida. No domina universalmente: aumenta varianza bajo curvatura simétrica. Con salto latente0,6, h→0 estima salto observado1,6, no efecto1. El baseline puede parecer bueno por cancelación de sesgos; tampoco valida identificación.

![Resultados sintéticos](results/comparison.png)

## Artefactos y límites

`src/`, `tests/`, `config.json`, `benchmarks/`, resultados crudos18.000filas, hashes/versiones/hardware, `notebook.ipynb` ejecutado, cinco referencias verificadas, `informe.md` con14puntos y≥3ideas comparadas, `MVP.md`.

No estima intervalos de confianza causales ni selecciona bandwidth usando datos reales; no implementa rdrobust/CCT ni RBC. No manipulación, fuzzyRD, running discreto, clustering, datos reales ni producto operacional. Las barras de error son Monte Carlo de la media, no IC de efecto en una muestra.
