# Simulación de un fondo de venture capital

Simulación Monte Carlo de un fondo de 30 inversiones con resultados de cola pesada. Estima la distribución del múltiplo del fondo y la probabilidad de devolver el capital, ilustrando la ley de potencias del venture.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy
python3 main.py
```

## Resultado de ejemplo

```text
Fondos simulados: 20000 | inversiones por fondo: 30
MOIC mediano: 2.43x | media: 2.82x
Percentiles MOIC (5, 25, 75, 95): [0.89 1.63 3.53 6.26]
P(MOIC >= 1x) = 92.6% | P(MOIC >= 3x) = 35.3%
TIR aproximada mediana (horizonte 8 anos): 11.7%
La mejor inversion aporta en mediana el 36% del valor del fondo
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
