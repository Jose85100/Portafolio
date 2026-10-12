# Modelo Black-Litterman

Combinación del equilibrio de mercado con opiniones del gestor mediante Black-Litterman: rendimientos implícitos de equilibrio, matriz de opiniones con incertidumbre, retornos posteriores y pesos resultantes.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
peso_mercado  retorno_equilibrio  retorno_posterior  peso_BL
EEUU                0.38              0.0438             0.0544   0.1895
Europa              0.17              0.0471             0.0646   0.3024
Japon               0.08              0.0370             0.0483   0.0672
Emergentes          0.10              0.0521             0.0748   0.2139
Bonos               0.27              0.0028             0.0030   0.2269
Cambio de peso vs mercado: {'EEUU': -0.19, 'Europa': 0.132, 'Japon': -0.013, 'Emergentes': 0.114, 'Bonos': -0.043}
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
