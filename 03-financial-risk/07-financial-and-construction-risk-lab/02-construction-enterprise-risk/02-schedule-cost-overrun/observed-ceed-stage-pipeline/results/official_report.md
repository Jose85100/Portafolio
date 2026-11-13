# Resultado reproducible: proxy de área paralizada/inactiva en CEED

El anexo describe área física censada en estados de obra; el cociente es un contexto sectorial. No mide atraso contractual, pérdida, mora, inventario no vendido ni desempeño de proyectos individuales.

## Corte más reciente (2026-T2)

| Destino | Área censada (m²) | Área paralizada/inactiva (m²) | Proxy sobre área censada (%) | Área en proceso (%) |
|---|---:|---:|---:|---:|
| Apartamentos | 23,736,406 | 4,081,721 | 17.20 | 72.68 |
| Casas | 2,956,403 | 1,290,735 | 43.66 | 44.29 |
| Vivienda (apartamentos + casas) | 26,692,809 | 5,372,456 | 20.13 | 69.54 |

## Comparación interanual del proxy

| Destino | 2025-T2 (%) | 2026-T2 (%) | Cambio (pp) |
|---|---:|---:|---:|
| Apartamentos | 18.80 | 17.20 | -1.60 |
| Casas | 46.21 | 43.66 | -2.55 |
| Vivienda (apartamentos + casas) | 22.08 | 20.13 | -1.95 |

## Interpretación

`Área paralizada o inactiva / área total censada` aproxima la fracción del área observada que DANE clasifica en ese estado. Puede activar revisión sectorial de exposición a obras detenidas y orientar escenarios de seguimiento; no se interpreta como tasa de incumplimiento ni como riesgo causal. El área total censada es el denominador explícito. Para vivienda, se suman metros cuadrados de apartamentos y casas antes de dividir; no se promedian porcentajes.

La población geográfica corresponde a la cobertura agregada del anexo Serie 20 áreas (57 municipios), que agrupa 14 áreas urbanas, cinco metropolitanas y Cundinamarca. No es una serie nacional de todos los proyectos ni se desagrega por empresa. El censo distingue obras culminadas, en proceso y paralizadas/inactivas; cambios de cobertura, clasificación y composición pueden mover el cociente.

Las observaciones de 2026 están dentro de la ventana de provisionalidad que DANE describe como de un año. El snapshot fue publicado el 14 de agosto de 2026. Los resultados pueden revisarse.

## Reproducción y linaje

Fuente: [DANE, Censo de Edificaciones, histórico](https://www.dane.gov.co/index.php/comunicados-y-boletines/construccion-y-vivienda/censo-de-edificaciones), archivo `anex-CEED-EstructuraSeriesDestino-IItrim2026.xlsx`, hoja `Serie 20 áreas (57_mpios)`, corte 1997–2026-T2. La edición extrae solo apartamentos y casas desde 2015-T4 hasta 2026-T2.

- 86 filas destino-trimestre (43 por destino), sin claves duplicadas ni valores de área faltantes en la selección.
- CSV incluye apartados por destino y una agregación reproducible de vivienda (apartamentos + casas), con shares de área en proceso y paralizada/inactiva.
- SHA-256 snapshot: `9446058a08ce93d0542c5061831beccfa7ef1a963f1eaf4fc26db7e61f3e24a1`.
- Ejecutar desde esta carpeta: `python3 scripts/build_companion.py` (requiere `openpyxl`, `pandas`, `matplotlib`).

## Brecha de validación

Para validar atraso contractual o pérdidas hace falta una muestra interna por obra con fechas planificadas y reales, presupuestos y cambios de alcance, hitos, financiación, preventas/ventas, costos incurridos y resultado final. El CEED solo permite comparar señal sectorial agregada; no calibra parámetros del modelo de sobrecosto/cronograma ni demuestra que la cuota de área paralizada anticipe incumplimientos.
