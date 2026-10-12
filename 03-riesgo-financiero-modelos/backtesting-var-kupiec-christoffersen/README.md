# Backtesting de VaR: Kupiec y Christoffersen

Backtesting de un VaR histórico al 99 % con ventana móvil sobre una serie con régimen de alta volatilidad. Aplica la prueba de cobertura incondicional de Kupiec y la prueba de independencia de Christoffersen.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
Observaciones: 1000 | excepciones: 17 | esperadas: 10.0 | tasa observada: 0.0170
Kupiec (cobertura):      LR=  4.09  p-valor=0.0431
Christoffersen (indep.): LR=  1.12  p-valor=0.2897
Excepciones consecutivas (n11): 1
```
