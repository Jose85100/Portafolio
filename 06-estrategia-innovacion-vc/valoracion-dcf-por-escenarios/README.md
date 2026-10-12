# Valoración de startups por escenarios

Valoración de una empresa en etapa temprana con flujo de caja descontado por tres escenarios (fracaso, base y éxito) ponderados por probabilidad, con sensibilidad a la tasa de descuento y al múltiplo de salida.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
Tasa de descuento: 30% (millones de USD)
  fracaso  prob=0.55 valor=   -0.46
  base     prob=0.35 valor=    4.14
  exito    prob=0.10 valor=   20.39
Valor esperado ponderado: 3.24
Sensibilidad del valor esperado a la tasa de descuento:
  tasa 20%:    5.61
  tasa 25%:    4.23
  tasa 30%:    3.24
  tasa 35%:    2.50
  tasa 40%:    1.95
```
