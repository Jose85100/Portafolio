# Backtesting de VaR: laboratorio y evidencia observada

El laboratorio controlado permite observar cómo Kupiec y Christoffersen reaccionan ante un régimen conocido. La aplicación oficial contrasta el mismo flujo sobre choques observados de tasa del U.S. Treasury, transformados en una exposición aproximada de duración constante.

## Aplicación oficial con observaciones de mercado

La serie diaria de rendimientos par a 10 años cubre 2024-01-02 a 2026-11-10. Se calculan 714 cambios, con ventana de 500 observaciones y backtest de 214 días fuera de tiempo (2026-01-06 a 2026-11-10). Sobre VaR histórico al 99% se observan 2 excepciones (2,14 esperadas); Kupiec UC p=0,923 y Christoffersen independencia p=0,846.

La falta de rechazo no valida el modelo: solo hay dos excepciones, por lo que la potencia del backtest es baja. El P&L usa una sensibilidad de duración modificada fija de 8; los rendimientos constantes interpolados no son retornos de un bono individual y la aproximación omite convexidad, carry, roll-down, cupón y riesgo de base.

- [Runner de la aplicación observada](official_application.py)
- [Resultados y excepciones](data/official/backtest.json)
- [Datos oficiales congelados y semántica](../var-es-tres-metodos/data/README.md)
- [Figura del backtest](reports/figures/treasury-var-kupiec-christoffersen.png)

## Aplicación sobre TES colombiano

Se añadió una segunda serie oficial: la tasa TES cero cupón COP a 10 años de BanRep. Con cambios consecutivos de rendimiento y duración constante de 8 años se arma una pérdida lineal proxy para un nocional supuesto de COP 1.000 millones. El backtest usa ventana móvil de 1.000 observaciones y deja fuera de muestra 1.913 intervalos desde el 2 de enero de 2019 hasta el 6 de noviembre de 2026. Se conservan seis configuraciones (VaR histórico y Gaussiano al 95%, 97,5% y 99%).

Para VaR histórico al 97,5% hubo 77 excepciones, frente a 47,8 esperadas; Kupiec UC p=0,000085 y Christoffersen independencia p<0,000001. Para el VaR Gaussiano al mismo nivel hubo 62 excepciones; Kupiec UC p=0,047 y Christoffersen independencia p<0,000001. Estos resultados muestran que el flujo permite detectar mala cobertura y agrupamiento en esta serie de factores; **no acreditan aptitud para límites ni para una cartera**. Dos cambios superiores a 100 pb dentro del holdout se mantuvieron y quedaron señalados para revisión de fuente. Las alertas antiguas (2003–2007) siguen sin reconciliación y están fuera de la ventana de evaluación.

La serie de BanRep es un punto de curva cero cupón estimado mediante Nelson–Siegel con insumos SEN/MEC, no el retorno total de un TES específico. Duración/nocional son hipotéticos; faltan convexidad, cupón, carry, roll-down, base, liquidez y transacciones. Véase la ficha metodológica del [companion TES para VaR/ES](../weighted-expected-shortfall-audit/observed-colombian-tes-rate-proxy/README.md). No hay posiciones ni P&L institucional que validen el modelo.

- [Runner TES](observed_colombian_tes_backtest.py)
- [Resumen, excepciones y pronósticos](data/official/colombian_tes/)
- [Figura de backtest](reports/figures/colombian-tes-var-backtest.png)

Reproducción desde la raíz del repositorio:

```bash
pip install numpy pandas scipy matplotlib
python3 03-financial-risk/02-market-and-model-risk/backtesting-var-kupiec-christoffersen/observed_colombian_tes_backtest.py
```

El runner valida hash, esquema y semántica del snapshot desde el companion de ES antes de construir retornos y pronósticos.

## Laboratorio controlado

El ejemplo original mantiene un proceso conocido con cambio de régimen para demostrar cobertura e independencia y verificar la implementación de las pruebas. Es evidencia de comportamiento bajo el diseño del experimento, no backtesting de una cartera real.

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

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.

Para reproducir la aplicación con datos oficiales, desde la raíz del proyecto:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```
