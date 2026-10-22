# Motor de minimización de pérdida por fraude

**S2 acotado: experimento sintético ejecutable.** Logit, gradient boosting, calibración posterior y detección de novedad alimentan una comparación de políticas. Un MILP asigna continuar, verificar o revisar bajo capacidad en minutos; implementa costo esperado entre escenarios y minimax finito.

Los cuatro especialistas de fraude siguen en S1. Sus cuatro familias de señales se representan mediante variables simuladas; no se han implementado validación documental, reconocimiento biométrico, GNN ni monitoreo de asesores. La función de entidades temporales es un primitivo probado de forma independiente y no genera las señales del benchmark.

## Reproducción

Desde esta carpeta, Python 3.11 o superior con las dependencias fijadas:

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run_experiment.py
```

El experimento regenera los archivos de `results/`. Las pruebas de optimización comparan contra enumeración exhaustiva independiente en 40 instancias/objetivos pequeños, además de contratos, límites y fuga temporal. La suite no requiere pytest. La repetibilidad numérica se interpreta con tolerancias entre plataformas, no como identidad de bytes de PNG.

## Organización

- `src/engine.py`: contratos, costos, primitivo temporal y optimizador binario.
- `src/models.py`: generador, imputación con entrenamiento, ajuste y calibración temporal.
- `run_experiment.py`: comparación de modelos, siete políticas, sensibilidad, CSV y figuras.
- `tests/test_engine.py`: oráculos independientes y contraejemplos.
- `results/experiment.json`: cortes, semilla, parámetros y versiones.
- `results/model_metrics.csv`, `reliability.csv`: discriminación y calibración.
- `results/policy_summary.csv`, `policy_daily.csv`, `decisions.csv`: costos agregados y decisiones.
- `results/effectiveness_sensitivity.csv`: políticas congeladas al variar eficacia.
- [Resultados e interpretación](RESULTS.md): cifras, condiciones y conclusiones negativas.

Los archivos CSV de decisiones solo contienen identificadores sintéticos. No es una interfaz para recibir clientes reales. El costo prevenible y la fricción son supuestos, no estimaciones causales. Para ver las capas y extensiones consulte [arquitectura](../ARCHITECTURE.md) y [técnicas y objetivo](../MODEL_AND_LOSS_METHODS.md).
