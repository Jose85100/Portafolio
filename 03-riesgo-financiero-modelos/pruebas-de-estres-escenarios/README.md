# Pruebas de estrés y estrés inverso

Pruebas de estrés de un portafolio con sensibilidades lineales a factores (acciones, tasas, tipo de cambio, spreads de crédito). Evalúa escenarios históricos e hipotéticos y resuelve el estrés inverso: qué choque de acciones produce una pérdida objetivo.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
acciones  tasa_10y_pb  usd_cop  spread_credito_pb  total_pct    perdida
crisis_2008         -17.10         0.74     3.00              -0.84     -14.20 -1419600.0
alza_de_tasas        -5.40        -1.55     0.96              -0.25      -6.24  -624200.0
choque_cambiario     -4.05        -0.37     3.60              -0.19      -1.01  -101100.0
recesion_local       -9.90         0.50     1.80              -0.52      -8.13  -812900.0
Peor escenario: crisis_2008 (-14.20% | -1,419,600)
Estres inverso: para perder 10.0% solo con acciones se requiere un choque de -22.2%
```
