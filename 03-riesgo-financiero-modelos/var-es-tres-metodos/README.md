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
