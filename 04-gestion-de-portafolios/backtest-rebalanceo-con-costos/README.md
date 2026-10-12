# Backtest de rebalanceo con costos de transacción

Backtest de diez años con retornos simulados que compara pesos iguales y mínima varianza con covarianza móvil, rebalanceo mensual y costos de transacción proporcionales a la rotación.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scipy
python3 main.py
```

## Resultado de ejemplo

```text
estrategia  retorno_anual  vol_anual  Sharpe  rotacion_total
     iguales         10.09%     11.63%    0.87            2.14
min_varianza         10.09%     11.63%    0.87            2.14
```
