# Asignación de capital por RAROC

Asignación del presupuesto de crédito entre segmentos maximizando el retorno ajustado por riesgo sujeto a un presupuesto de capital y topes por segmento, resuelto con programación lineal.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scipy
python3 main.py
```

## Resultado de ejemplo

```text
segmento  utilidad  capital  raroc  tope  asignacion
    consumo     0.070     0.10 0.7000  0.30      0.3000
    tarjeta     0.100     0.13 0.7692  0.15      0.1500
   vehiculo     0.053     0.08 0.6625  0.30      0.2667
hipotecario     0.041     0.05 0.8200  0.40      0.2833
       pyme     0.052     0.11 0.4727  0.20      0.0000
corporativo     0.033     0.07 0.4714  0.35      0.0000
Estado del optimizador: Optimization terminated successfully. (HiGHS Status 7: Optimal)
Utilidad esperada sobre cartera: 0.0618 | capital usado: 0.0850 de 0.085 | RAROC: 0.726
```
