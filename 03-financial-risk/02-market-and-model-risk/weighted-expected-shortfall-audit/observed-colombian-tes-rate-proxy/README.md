# VaR y Expected Shortfall sobre un factor TES colombiano

## Pregunta y uso

¿Qué VaR y Expected Shortfall empíricos produce el motor de ES ponderado cuando se aplica a cambios observados de la tasa TES cero cupón en pesos a 10 años? Este companion conecta el cálculo numérico de `src.tail` con un factor de mercado oficial colombiano. La salida representa una **posición hipotética de duración constante**; no es P&L de bono, cartera institucional ni backtest.

## Fuente y linaje

Fuente primaria: [Banco de la República, serie 15274](https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/220002/tasas_interes_cero_cupon_tes/), “Tasa de interés Cero Cupón, Títulos de Tesorería (TES), pesos - 10 años”. El snapshot reporta periodicidad diaria, unidad porcentual y 5.801 observaciones del 2 de enero de 2003 al 6 de noviembre de 2026; el último cargue que informa la ficha es el 9 de noviembre de 2026.

BanRep indica que la tasa a 10 años se deriva de la curva cero cupón estimada con Nelson–Siegel y de información de operaciones negociadas y registradas en SEN y MEC ([ficha metodológica TES](https://www.banrep.gov.co/en/node/41443)). Por eso el factor refleja condiciones de mercado, pero sigue siendo un punto de una curva estimada, no la rentabilidad total de un TES específico.

El snapshot público JSON se conserva en `data/raw/banrep_tes10_official.json` para reproducir exactamente la transformación. SHA-256: `335739330f675690c418a06d464b97a39f8b7326a2d3c7b6711647e58cd33f1b`; tamaño: 312.401 bytes. `data/source_reference.json` guarda fuente, serie, periodo, unidad, método y supuestos. Se valida el hash, ID/nombre de serie, unidad, frecuencia, número de puntos, fechas ordenadas y ausencia de fechas duplicadas.

## Transformación a P&L hipotético

Para el cambio entre dos observaciones consecutivas, se aproxima la pérdida de una posición larga en TES mediante duración modificada fija:

```text
Δy_bp = 100 × (y_t − y_(t−1))                  # y está expresado en porcentaje
Pérdida proxy_t = D_mod × (Δy_bp / 10.000) × N
```

El escenario fija duración modificada `D_mod = 8` años y nocional `N = COP 1.000.000.000`. Un alza de tasas produce pérdida proxy positiva; una caída produce ganancia proxy negativa. Los cambios se miden por intervalo publicado; no se ajusta por los días calendario entre observaciones ni se anualiza.

Cada intervalo observado recibe probabilidad igual. El runner calcula VaR al 97,5% como inversa izquierda de la CDF y ES como integral de la masa superior con fracción en el átomo de frontera. Antes de guardar resultados, compara ambas cifras con un cálculo independiente por estadísticos de orden y suma de masa fraccionaria.

## Resultado y límites

En la vintage congelada, el runner obtiene **VaR 97,5% de COP 25,60 millones** y **ES 97,5% de COP 56,76 millones** para el nocional hipotético de COP 1.000 millones y duración 8. La cola empírica contiene 145 intervalos completos de los 5.800 cambios. El motor y la integración independiente coinciden antes de escribir resultados.

La serie presenta saltos y reversos de varios cientos de puntos básicos al comienzo: por ejemplo, −511 pb del 23 al 24 de diciembre de 2004 y +514 pb del 24 al 27 de diciembre. Se incluyen en el resultado y afectan la cola; no se eliminaron ni winsorizaron porque no se verificó una corrección oficial del vintage. El archivo `results/largest_yield_changes_for_review.csv` muestra los veinte cambios absolutos mayores. El flag de cambios superiores a 100 pb marca 34 intervalos para cotejo manual; no altera la muestra ni constituye una regla de limpieza aprobada. El máximo cambio convertido a la exposición hipotética equivale a COP 411,2 millones de pérdida lineal. Así, los cálculos son reproducibles para este snapshot, pero **requieren reconciliar esos puntos con BanRep antes de interpretarlos económicamente**.

### Revisión de calidad de los saltos históricos

Se contrastó la observación con la ficha oficial de la serie 15274 y con las publicaciones/metadatos públicos consultables de BanRep. En el JSON archivado, `feErratas` figura como `-`; la definición confirma que son tasas de una curva cero cupón estimada por Nelson–Siegel a partir de operaciones SEN/MEC. La ficha no identifica una corrección para estas fechas. El [catálogo público de series de BanRep](https://totoro.banrep.gov.co/estadisticas-economicas/faces/pages/Buscador.xhtml) publica la serie COP 10 años diaria para el mismo periodo, pero no proporciona por sí mismo un vintage histórico independiente con el que reconstruir las cifras de 2003–2004.

BanRep también registra una modificación de datos publicada el 15 de abril de 2020 por actualización de insumos para el cálculo de betas de la curva Nelson–Siegel de TES **denominados en UVR** ([nota oficial de descargas y consultas](https://www.banrep.gov.co/en/print/pdf/node/50444)). Esa nota es evidencia de que algunos insumos de curvas pueden revisarse, pero su alcance declarado es UVR; no demuestra una revisión ni explica los saltos de la serie COP 10 años 15274. Las series mensuales o tasas promedio disponibles tampoco son una réplica independiente de esta serie diaria y no permiten validar cada punto.

Conclusión de la revisión: los cambios de −511/+514 pb del 23–27 de diciembre de 2004 y otros saltos de 2003 siguen siendo **alertas de calidad sin resolver**, no errores confirmados ni movimientos económicos confirmados. Se conserva íntegro el snapshot y la cifra reportada, sin filtrado. El VaR/ES resultante es válido como reproducción mecánica de los bytes congelados; su interpretación como riesgo de mercado requiere una respuesta de BanRep o un vintage diario alternativo oficial que confirme los valores y su tratamiento. Hasta entonces, no se debe usar esta cola para calibrar límites, validar una cartera o inferir shocks plausibles.

El snapshot contiene una serie larga, pero los resultados dependen del vintage. La dependencia temporal entre cambios y los intervalos de fin de semana/festivos hacen que los 5.800 cambios no sean escenarios iid ni observaciones idénticas en horizonte; el mayor salto entre fechas fue de seis días calendario. La cola empírica es una descripción histórica de la posición estilizada, no una estimación validada de riesgo institucional.

La duración y el nocional son supuestos, no posiciones observadas. La aproximación lineal no incorpora convexidad, flujos de cupón, carry, roll-down, forma de curva, base, FX, costos de negociación o diversificación. La aplicación permite revisar la cola empírica de un shock de tasa sobre una exposición mecánica; no valida un modelo de VaR/ES, sus parámetros, límites o desempeño para una cartera. Para ello se requieren posiciones y sensibilidades fechadas, precios/P&L realizados y pronósticos VaR/ES versionados para la misma cartera y horizonte, además de validación independiente.

## Reproducción

Requiere Python 3, `numpy`, `pandas` y `matplotlib`. El motor `src.tail` está en el directorio padre. Desde esta carpeta:

```bash
python3 scripts/build_observed_es.py
```

Se puede indicar otra copia byte a byte idéntica del snapshot:

```bash
python3 scripts/build_observed_es.py --input "/ruta/banrep_tes10_official.json"
```

Artefactos:

- `results/colombian_tes_daily_proxy.csv` — cambios de tasa e hipótesis de pérdida COP por intervalo;
- `results/largest_yield_changes_for_review.csv` — veinte cambios absolutos mayores con fechas, tasas y pérdidas proxy para cotejo de fuente;
- `results/colombian_tes_es_metrics.csv` — VaR y ES al 97,5%;
- `results/colombian_tes_es_summary.json` — métricas, hashes, conciliación independiente y límites;
- `figures/colombian_tes_es_proxy.png` — factor observado y distribución de pérdida proxy.
