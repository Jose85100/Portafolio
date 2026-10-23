# Innovation EVSI Gate

Decidir **experimentar, escalar o detener** una iniciativa IA antes de comprometer despliegue. Componente S2 sintético dentro del programa 20 (el programa completo conserva S1). Un beta-binomial exacto valora un piloto y resta su costo; la decisión no usa la probabilidad verdadera oculta.

## Reproducir

Desde esta carpeta, Python 3.12 y acceso al índice de paquetes:

```bash
bash run.sh
```

Crea `.venv`, instala versiones fijadas, ejecuta tests/cobertura, ruff, mypy, benchmark y notebook. Con entorno ya instalado: `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`. Dependencias transitivas no están bloqueadas por hash. No se requiere API ni información privada. Linux es el entorno medido (`resource.ru_maxrss` tiene unidades distintas en macOS).

El notebook se ejecuta realmente de arriba abajo con IPython en un namespace nuevo y captura de salidas. El kernel Jupyter TCP no pudo arrancar aquí por restricción de sockets (2026-10-23); no se afirma validación de kernel. En un entorno con Jupyter instalado, `NOTEBOOK_KERNEL=1 bash run.sh` usa nbclient. Cada cuaderno registra el modo real en metadatos.

## Resultado sintético

| Política | Observaciones | Valor esperado neto |
|---|---:|---:|
| Decidir hoy | 0 | 0,00 |
| Piloto fijo | 100 | 5.138,22 |
| Mejor candidato EVSI | 50 | 5.140,42 |

La mejora frente a hoy es 5.140,42 unidades sintéticas; frente al piloto fijo es solo 2,19. No es una demostración de rentabilidad empresarial. EVSI bruto 5.490,42 ≤ EVPI 6.019,74. Oracle Monte Carlo 200.000 réplicas: 5.153,61 ± 18,87 (un error estándar), consistente con enumeración.

`config.json` define hipótesis, umbral (+1.000), prior, grid, población futura, costos, semilla y réplicas. `src/evsi.py` no depende de NumPy/SciPy. `results/` conserva CSV diseños, sensibilidad, 200 bloques MC, figura, JSON y cobertura. `notebook.ipynb` explica fórmulas y resultados. `informe.md` contiene análisis crítico y fuentes.

## Decisión y alcance

El piloto es una muestra separada de la población futura fija; no consume despliegue ni recibe beneficio operativo. Son datos IID de éxito operativo, **no uplift causal**. Requiere beneficio/costos conocidos y prior transferible. Requiere rediseño si hay drift, dependencia, selección o costos omitidos. La política elige el mejor tamaño **del grid**, no un óptimo continuo ni una estrategia secuencial. No certifica desempeño operativo ni regulatorio.

## Ampliación del notebook — 23 de octubre

El notebook incorpora fórmulas, diccionario de variables en contexto, reconstrucción de cálculos, sensibilidad y casos negativos. `run.sh` conserva esta ampliación después de regenerar el estudio original. La extensión se mantiene en `scripts/deepen_20261023_notebooks.py` y `scripts/research_depth_experiments.py` desde la raíz; las celdas realmente se ejecutan y guardan sus salidas. [Revisión de alcance](../../../reviews/2026-10-23-alignment/README.md).

[Revisión académica y criterios de cierre](ACADEMIC_REVIEW.md): fuentes publicadas, fórmulas en el notebook y extensiones experimentales.
