# Capital de Vasicek frente a Monte Carlo

Fórmula de un factor de Vasicek (ASRF) para la pérdida no esperada al 99,9 % y su verificación con una simulación Monte Carlo de un portafolio homogéneo finito, con distintos niveles de correlación.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
PD=0.02, LGD=0.45, deudores=2000, nivel 99.9%
  rho    Vasicek  Monte Carlo
 0.03     0.0187       0.0193
 0.08     0.0402       0.0405
 0.15     0.0703       0.0711
 0.24     0.1115       0.1148
```
