# MFA WDI: nota de evidencia observada

## Resultado

Esta edición aplica el motor MFA a una sección transversal de indicadores de países del World Development Indicators. El snapshot local contiene 6.270 registros largos de 26 indicadores. El API devuelve 261 códigos ISO3 en el archivo de observaciones porque también incluye agregados; la metadata analítica del notebook conserva 217 economías no agregadas. Con cobertura mínima de 85% se analizan 171 países y se excluyen 46; 107 tienen los 26 valores. Se imputan 112 celdas de 4.446 (2,52%). El detalle por fuente, ventana, grano y hash está en [`datos/manifest.json`](../datos/manifest.json).

El primer autovalor MFA es 4,37 de un máximo de 5: el primer eje resume 45,1% de la inercia. Los cinco temas aportan 19–21% a ese eje. El eje se asocia con la categoría externa de ingreso (Spearman 0,92), aunque ingreso no entra como variable activa. Los tres primeros ejes tienen un subespacio bootstrap más estable que cuatro ejes; en el tercero hay solapamiento de intervalos con el segundo y su orientación es menos precisa.

## Sensibilidad y decisión

Preparación alternativa (transformaciones, casos completos, niveles de imputación y umbrales de cobertura) conserva la configuración global: RV 0,98–1,00 y correlación absoluta del primer eje de al menos 0,994. Esto respalda estabilidad del eje común **dentro de estas especificaciones**; no resuelve la selección no aleatoria de datos faltantes ni la mezcla de años.

La partición k=2 alcanza Jaccard mínimo 0,96 y silhouette 0,47. Para k=3, el Jaccard mínimo cae a 0,63, la mediana ARI de sensibilidad es 0,72, y 36 de 171 países (21%) tienen probabilidad máxima de pertenencia menor a 70%. Los perfiles de países se aproximan a un continuo. La salida recomendada es comunicar el eje y la partición binaria robusta como resumen; si se usa k=3, mostrar pertenencias y fronteras difusas.

La evidencia permite comparar estructuras descriptivas en el snapshot WDI. No valida causalmente políticas, no ordena el desempeño presente y no demuestra capacidad predictiva. Antes de usarla para focalización o asignación de recursos se requiere un propósito de decisión concreto, vintages sincronizados, metadatos y fuentes primarias por indicador, validación con equipos regionales y análisis de sensibilidad bajo la población real de uso.

## Procedencia y límites de versionado

El proveedor es el Banco Mundial, API V2 de WDI, consultada históricamente para 2015–2022. Los CSV locales se congelaron en el repositorio, pero el proceso original no conservó la hora de descarga ni el vintage de revisión que devolvió el API. El manifiesto actual incorpora hashes de los archivos y la fecha de auditoría local; esa fecha no se presenta como fecha de extracción. WDI integra indicadores de distintas fuentes estadísticas. Al actualizar, mantener las notas de cada indicador y verificar la licencia aplicable a sus datos upstream; la política general de datos abiertos del Banco Mundial se describe en [Data Access and Licensing](https://datacatalog.worldbank.org/public-licenses).

## Figuras

Las cinco figuras reproducibles/exportables del notebook están en [`figures/`](figures/). El exportador selecciona las salidas de las celdas 5, 19, 25, 28 y 35 del notebook ejecutado; el código analítico completo permanece en el notebook.
