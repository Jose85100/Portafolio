# Cohortes de retención, LTV y CAC

Análisis de cohortes de suscripción mensual: retención por antigüedad, churn, LTV, relación LTV/CAC y meses de recuperación del CAC, con una cohorte deteriorada a propósito para mostrar cómo se detecta.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Retencion por cohorte (meses 1, 3, 6, 12):
       1      3      6      12
C1  0.892  0.771  0.670  0.516
C2  0.891  0.770  0.672  0.539
C3  0.886  0.778  0.689  0.553
C4  0.876  0.765  0.669  0.551
C5  0.891  0.774  0.662  0.530
C6  0.818  0.623  0.490  0.333
C7  0.884  0.745  0.643  0.498
C8  0.877  0.763  0.679  0.565
    churn_mensual     LTV  LTV/CAC  payback_meses
C1           0.05  581.60     2.24           8.33
C2           0.05  621.52     2.39           8.33
C3           0.05  647.74     2.49           8.33
C4           0.05  643.90     2.48           8.33
C5           0.05  605.46     2.33           8.33
C6           0.09  356.32     1.37           8.33
C7           0.06  552.79     2.13           8.33
C8           0.05  671.50     2.58           8.33
Cohorte con menor LTV/CAC: C6 (1.37); regla usual: >= 3
```
