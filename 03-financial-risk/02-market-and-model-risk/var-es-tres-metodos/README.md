# VaR y Expected Shortfall por tres métodos

Cálculo de VaR y Expected Shortfall de un portafolio con simulación histórica, método paramétrico normal y ajuste t de Student, sobre retornos con colas pesadas. Muestra cuánto subestima el supuesto normal.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
Valor del portafolio: 1,000,000 | observaciones: 2500
 nivel       metodo          VaR           ES
  0.95    historico       14,974       22,541
  0.95       normal       15,889       19,989
  0.95    t-student       14,792       22,352
  0.99    historico       27,222       35,472
  0.99       normal       22,576       25,901
  0.99    t-student       26,485       36,823
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.


## Contrato histórico revisado — 2026-10-18

`main.py:historico` usa VaR empírico sin interpolación y ES de masa fraccionaria exacta. El caso de 99 ceros y pérdida 100 al 97.5% devuelve ES=40. La función `historico_legacy_conditional` preserva el antiguo promedio condicionado como comparador deliberado del benchmark; no es la API por defecto. Importar el módulo ya no ejecuta la demo ni ajusta modelos automáticamente.

El método t usa una distribución predictiva ajustada y 400.000 draws con semilla explícita; no es la misma medida empírica sobre las n observaciones originales. El notebook conserva su desarrollo didáctico y sus comparaciones de estimación.
