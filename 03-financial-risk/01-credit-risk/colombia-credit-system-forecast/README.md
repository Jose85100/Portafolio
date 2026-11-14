# Colombia — Modelo agregado de calidad de cartera

**Madurez: investigación reproducible; no operativo.** Laboratorio para estudiar si la calidad de cartera por vencimiento de los establecimientos de crédito puede estimarse con indicadores financieros y macroeconómicos públicos. La evidencia y resultados se encuentran en [el informe](reports/informe.md); [especificación y controles](docs/modelo-y-gobierno.md) documenta la construcción y sus límites.

La ampliación [territorial y económica](reports/territorial/informe.md) integra datos municipales SFC, coordenadas DIVIPOLA, proyecciones de población e IPC mensual del DANE e inflación anual del Banco Mundial. Compara cortes de junio de 2023–2026, calcula el crecimiento ajustado por IPC y descompone por tipo de entidad una brecha entre fuentes SFC. Es descriptiva y conserva las observaciones sin homologar en cuarentena. La diferencia entre fuentes aún no tiene causa identificada.

El [análisis multivariado](reports/multivariado/informe.md) añade PCA, dos factores comunes, K-means y mezcla gaussiana sobre indicadores de cartera y variables económicas. Sus grupos describen meses agregados, no categorías de riesgo individual; los parámetros se ajustan en 2017–2022 y se examina su estabilidad posterior.

## Pregunta y alcance

Para un mes t, estimar el porcentaje `100 × saldo vencido / saldo bruto` para el total de establecimientos de crédito **sin instituciones oficiales especiales**, bajo el supuesto retrospectivo de que las cifras hasta t−2 son conocidas al cierre de t−1. La SFC define vencimiento por modalidad; es una razón de saldos en una fecha y no equivale a PD individual, transición de mora, pérdida esperada ni diagnóstico de solvencia.

La muestra es nacional agregada; incluye series de modalidades comercial, consumo, vivienda y microcrédito, pero no todos los sectores del sistema financiero. Fuente principal: [SFC, series NIIF desde 2016](https://www.superfinanciera.gov.co/publicaciones/10086287/), archivo agregado «Total Entidades Establecimiento de Crédito», hoja `CarteraPorModalidad`; serie procesada por la SFC el 27 de octubre de 2026, datos mensuales de enero de 2016 a septiembre de 2026. La SFC advierte que las cifras NIIF no son comparables directamente con los datos de 2014 y anteriores. TRM: [Datos Abiertos / Superintendencia Financiera](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3), valor vigente al cierre de cada mes, en pesos por dólar.

Se preservan las descargas y un manifiesto SHA-256 en `data/raw/`; la transformación y conciliación crean `data/processed/serie_mensual.csv`. `results/` contiene métricas, resumen y predicciones; `reports/figures/` conserva las gráficas. No hay datos individuales ni predicciones de clientes.

## Validación

El laboratorio compara persistencia, tendencia lineal, regresión Ridge y gradient boosting. Usa variables financieras y TRM rezagadas, normalización ajustada solo en entrenamiento y una ventana de entrenamiento expansiva por mes. Los años 2020–2022 se usan para selección, y enero de 2023 a septiembre de 2026 para evaluación posterior. La selección, establecida por menor MAE en desarrollo, eligió persistencia. El modelo de boosting mostró menor error en la evaluación posterior, pero esa observación no constituye una nueva selección validada.

**Límite esencial:** los archivos descargados hoy pueden contener revisiones y no prueban qué información fue publicada en cada fecha histórica. El rezago de dos meses es una hipótesis, no un calendario comprobado. La evaluación es retrospectiva y ya fue examinada; se requiere una nueva prueba independiente con versiones originales y fechas de publicación antes de uso real.

## Ejecución

Con Python y `requirements.txt` instalados, desde esta carpeta:

```bash
python3 src/model.py
python3 src/territorial.py
python3 src/macro.py
python3 src/contexto_economico.py
python3 src/modelo_ipc.py
python3 src/analisis_multivariado.py
python3 -m pytest tests -q
```

`src/download.py` actualiza ambas fuentes y sus hashes. Actualizar puede cambiar el histórico, el corte y las métricas; conservar la instantánea anterior si es necesario comparar versiones. El script de modelación actual exige exactamente la estructura y cobertura esperadas y falla ante datos incompletos o saldos inconsistentes. Antes de redistribuir datos, revisar atribución y condiciones de la fuente.

Para actualizar fuentes territoriales y macroeconómicas se usan `src/download_territorial.py`, `src/download_contexto.py` y `src/macro.py --download`. Las consultas, las fechas y los hashes están en `data/territorial/raw/`; el procesamiento guarda municipios, cobertura, cuarentena y comparaciones en `data/territorial/processed/`. El IPC se evalúa en challengers exploratorios, sin reseleccionar el modelo; los datos territoriales no entran al backtest nacional. Faltan fechas históricas de publicación por versión.
