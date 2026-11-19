# Transiciones empíricas de rangos de IRL: benchmark retrospectivo

Se estima un modelo de transición mensual entre rangos del indicador de liquidez de la SFC y se compara con dos referencias probabilísticas en cortes posteriores. El objetivo es evaluar la persistencia **del indicador observado**; no estima probabilidad de incumplimiento, agotamiento de caja ni costos de liquidación. La hipótesis de Markov se usa como aproximación y no se da por validada.

## Datos y alcance

Fuente: [SFC, Indicador de Riesgo de Liquidez](https://www.superfinanciera.gov.co/publicaciones/10108220/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-de-riesgo-de-liquidez-indicador-de-riesgo-de-liquidez-irl-10108220/), datos mensuales de entidades reportantes. Se reutiliza el [derivado por entidad y mes y su ficha de procedencia](../observed-sfc-irl/README.md), descargado el 10-nov-2026, con 1.438 registros entre marzo de 2020 y diciembre de 2022. El runner exige SHA-256 `d4b1e8eb6bb1606abd9c5f0fed572d00a19d2cd5a4da94d83eb4b5bb1c801929`, IRL finito y no negativo, RLN positivo y clave entidad-mes única. Utiliza el IRL publicado en porcentaje, no lo recalcula con datos redondeados. Su valor mínimo en esta muestra es 112,78%; **no hay observaciones inferiores a 100%**. La muestra y el filtro del archivo pueden limitar esa cobertura; no cabe evaluar eventos de incumplimiento con este corte.

Para cada entidad `e` y mes `t` se define un estado descriptivo: `s=0` si IRL<150%, `s=1` si 150%≤IRL<250%, y `s=2` si IRL≥250%. Los cortes 150 y 250 son **ilustrativos**, no límites regulatorios, y se eligieron para este ejercicio; otras particiones pueden producir otros resultados. Las filas son transiciones entre meses calendario consecutivos del mismo código. Se excluye una transición si falta el mes anterior; no se imputa. Un mismo código puede experimentar cambios societarios que aquí no se reconcilian. El IRL puede cambiar por su numerador o denominador: un cociente alto con RLN pequeño no garantiza liquidez en efectivo.

## Modelo y fórmulas

Para transición observada `s(e,t−1)=i` y `s(e,t)=j`, sea

\[
N_{ij}=\sum_{e,t\in T_{train}} \mathbf{1}\{s_{e,t-1}=i,\ s_{e,t}=j\},\qquad N_i=\sum_j N_{ij}.
\]

El modelo ajusta una matriz común por máxima frecuencia suavizada con `α=0,5` por celda:

\[
\widehat P_{ij}=\frac{N_{ij}+\alpha}{N_i+3\alpha}.
\]

El suavizado evita probabilidades cero en celdas sin observaciones; no incorpora información externa ni corrige dependencia. Se comparan:

1. **Distribución incondicional**: \(\widehat q_j=(\sum_i N_{ij}+\alpha)/(N+3\alpha)\); ignora el estado previo.
2. **Persistencia común**: estima \(\widehat\epsilon=(\sum_{i\ne j}N_{ij}+\alpha)/(N+2\alpha)\). Pronostica \(1-\widehat\epsilon\) al estado previo y \(\widehat\epsilon/2\) a cada alternativa. La tasa común de cambio se ajusta solo en entrenamiento.
3. **Transición condicional**: usa \(\widehat P_{ij}\), permitiendo riesgo de salida y dirección distintos por estado.

Entrenamiento: transiciones cuyo mes destino está entre abril de 2020 y diciembre de 2021. Prueba: mes destino enero–diciembre de 2022. La historia previa a enero se utiliza únicamente para el estado inicial de enero. Cada método se puntúa sobre los mismos 521 pares entidad-mes; se cuenta cada par por igual, sin ponderar por activos.

Para probabilidad pronosticada `p_k` y estado observado `y`, el Brier multiclase usado es

\[
BS = \frac{1}{n}\sum_{r=1}^n\sum_{k=0}^2 (p_{rk}-\mathbf 1\{y_r=k\})^2, \qquad
LL = -\frac{1}{n}\sum_{r=1}^n\log p_{r,y_r}.
\]

No se divide el Brier por el número de clases; para tres categorías está entre 0 y 2. Menor Brier o log loss indican mejor desempeño probabilístico en esta muestra, no una validación de flujos de caja ni de riesgos de cola.

## Resultados

Con 868 transiciones de entrenamiento y 521 de prueba (45 entidades distintas en cada período), el suavizado da:

| Estado de origen | Destino <150% | Destino 150–<250% | Destino ≥250% |
|---|---:|---:|---:|
| <150% | 0,6723 | 0,3220 | 0,0056 |
| 150–<250% | 0,0926 | 0,7815 | 0,1259 |
| ≥250% | 0,0011 | 0,0913 | 0,9076 |

Las cifras son frecuencias condicionales suavizadas, no probabilidades regulatorias ni pronósticos institucionales calibrados. La tasa común de cambio entrenada para la referencia de persistencia es 0,1617.

| Método | Brier multiclase | Log loss |
|---|---:|---:|
| Incondicional | 0,6474 | 1,0871 |
| Persistencia común | 0,3474 | 0,6522 |
| Transición condicional | 0,3296 | 0,5627 |

La diferencia Brier pareada incondicional menos transición es 0,3179. Se presenta un intervalo percentil exploratorio [0,2291; 0,4064] mediante 2.000 remuestreos de **entidades completas**, semilla 42. Es condicional a la matriz ya ajustada; no incorpora incertidumbre de entrenamiento ni selección de rangos, y solo contempla dependencia dentro de entidad, no shocks comunes entre entidades. No es evidencia de estabilidad fuera de 2022 ni permite concluir que la diferencia frente a persistencia sea estadísticamente distinta de cero.

El snapshot se obtuvo en 2026 y no documenta las fechas de publicación o revisiones históricas de cada fila. Aunque las variables predictoras solo usan meses anteriores, la evaluación **no prueba disponibilidad point-in-time**. La inclusión de entidades puede variar por período. El horizonte es de un mes y faltan flujos, balances y eventos de iliquidez para estudiar primera ruptura, contagio o fire sales. Resultados de la matriz, conteos y evaluación se preservan en [results.json](results.json).

## Reproducción

Con Python estándar, desde la raíz:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/irl-transition-benchmark/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/irl-transition-benchmark -v
```

Las pruebas incluyen límites de clase, discontinuidades, conteos manuales, puntuaciones probabilísticas, duplicados y reproducibilidad del remuestreo. Los vínculos de fuente, universo, huellas y exclusiones son necesarios para actualizar el corte; cambiar el snapshot requiere nueva validación de hash y comparabilidad.
