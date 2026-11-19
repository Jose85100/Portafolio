# Referencias retrospectivas para la mora agregada de ICETEX

Este ejercicio compara dos referencias trimestrales de la **proporción de créditos activos con mora mayor a 90 días**, por fase Estudios o Amortización. No estima cosechas, transiciones ni PD individual. Para cada fase y corte se suman numerador y denominador entre departamentos y se divide el total; no se promedian tasas departamentales.

## Fuente y calidad

Se reutiliza el snapshot curado de [ICETEX, Comportamiento de Cartera y Crédito](https://www.datos.gov.co/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir) con los términos y el linaje de [la ficha del snapshot](../data/README.md): descarga del 10-nov-2026, 1.237 filas, 18 cortes entre marzo de 2022 y septiembre de 2026. El runner exige SHA-256 del derivado `c856d4e8ac26b63347d18e722f5467a7f9421dce9b01ab79d3aad4ca5f13ffcf`, llaves fecha × departamento × fase únicas, evidencia observada y conteos válidos. El corte de junio de 2025 fue excluido íntegramente por fallas de conciliación; no se interpola.

## Diseño y resultados

El ejercicio evalúa retrospectivamente cortes desde 2024, con al menos cuatro observaciones históricas. `previous_quarter` usa el corte anterior solo si es el trimestre calendario inmediato. `expanding_mean` usa la media de los cortes anteriores disponibles y evalúa exactamente las mismas fechas que la referencia anterior. Se excluye septiembre de 2025 porque no existe un corte válido de junio. Las tasas de las fases están ponderadas por número de créditos; el promedio temporal es simple. Cada corte aporta el mismo peso al error absoluto medio (MAE), expresado en puntos porcentuales.

| Fase | Cortes evaluados | MAE trimestre previo (pp) | MAE media histórica (pp) |
|---|---:|---:|---:|
| Amortización | 9 | 1,905 | 2,227 |
| Estudios | 9 | 1,502 | 0,793 |

Son comparaciones exploratorias en una muestra pequeña; la elección posterior de una referencia no acredita capacidad predictiva futura. Las fechas son de observación, no fechas verificadas de publicación: el snapshot descargado en 2026 **no demuestra qué dato estaba disponible en cada momento**, por lo que no es un backtest operativo point-in-time. Los cambios de cartera y composición pueden afectar la serie; no se sigue a los créditos individuales ni se mide default nuevo, recuperación, LGD, EAD, pérdida o desempeño de un modelo de originación.

## Reproducción

Con Python estándar, desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/01-credit-risk/observed-data-proxies/stock-baseline/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/01-credit-risk/observed-data-proxies/stock-baseline -v
```

Los valores por corte y el hash constan en [results.json](results.json). Datos: ICETEX, Fuente: Portal de Datos Abiertos www.datos.gov.co. Para validar PD o cosechas hacen falta registros longitudinales autorizados, fecha de originación, definición de default, migraciones y fechas de disponibilidad de cada versión de datos.
