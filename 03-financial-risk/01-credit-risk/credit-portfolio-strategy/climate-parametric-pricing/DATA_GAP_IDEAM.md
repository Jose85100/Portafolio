# Brecha de datos — índice climático y riesgo de base

## Hallazgo

El laboratorio del proyecto continúa siendo sintético. Se revisó el layer oficial IDEAM [`StoryMaps_IDA/Datos_Precipitacion/MapServer/0`](https://visualizador.ideam.gov.co/gisserver/rest/services/StoryMaps_IDA/Datos_Precipitacion/MapServer/0), titulado `precipitacion_diaria`. El snapshot local del layer contiene 629 estaciones y campos de estación, municipio, `DATO`, categoría, tecnología y geometría. **No contiene un campo de fecha ni un periodo de observación**; por ello no forma una serie diaria histórica reproducible y no basta para estimar frecuencia de trigger o prima.

Hashes del snapshot de metadatos y de las features inspeccionadas:

| Artefacto de staging externo | SHA-256 |
|---|---|
| `ideam_arcgis/precipitacion_diaria_metadata.json` | `489d9ca0ca81e2913502ce9175df2dbdb4df85bb9b17a475dc417c781c1ea24f` |
| `ideam_arcgis/precipitacion_diaria_features.geojson` | `60995556b1814cf618644e3abb18b88c99dbc0ee545929a64c4ee72d44350b54` |

El archivo de features no se copia al proyecto. Existe un servicio IDEAM de series hidrometeorológicas y una capa de cartografía de precipitación mensual; su descubrimiento no prueba disponibilidad de historia diaria homogénea para el área asegurada. Se requiere recuperar una serie autorizada y conservar fecha de consulta, estación, periodo, unidades, cambios de instrumento, faltantes y hash.

## Actualización: serie NASA POWER de apoyo (2026-11)

Ya se procesó un snapshot diario NASA POWER para diez coordenadas urbanas de Colombia en [observed-nasa-power-climate-index](observed-nasa-power-climate-index/). La serie cubre 2000-01-01 a 2026-07-19 y sus hashes, parámetros y perfil de calidad están en `results/source_quality_manifest.json`. La precipitación anual 2020–2025 se compara con el P10 por ciudad del periodo 2000–2019; tres de diez ciudades quedan bajo ese umbral en dos de los seis años recientes.

Esto resuelve la brecha de **exploración de una señal meteorológica fechada**, pero no la brecha de datos del producto asegurado: POWER ofrece estimaciones/reanálisis cuadriculados, no observaciones del pluviómetro del predio, y diez puntos urbanos no representan zonas agrícolas. Tampoco hay exposición, daños, pagos ni mora vinculados. Así que no se calibra prima/gatillo, no se mide riesgo de base ni se valida efecto sobre crédito. La serie IDEAM fechada y los resultados económicos siguen siendo necesarios para elevar el estado de evidencia.

## Datos mínimos para avanzar

1. Precipitación diaria o mensual fechada, por estación, con unidades y flags de calidad; periodo largo y continuo, con reglas de agregación y georreferencia documentadas.
2. Definición de cultivo/actividad, ubicación, calendario, superficie y exposición asegurada.
3. Pérdidas o pagos observados, enlazables en lugar y tiempo, para cuantificar riesgo de base. Sin ellos solo se puede describir la señal climática, no la suficiencia actuarial.
4. Separación temporal y geográfica, criterios actuariales de aceptación y revisión independiente antes de hablar de tarifa.

Hasta obtener esos insumos, no calcular gatillos óptimos, correlación índice-daño, prima, TVaR real, asequibilidad ni efecto sobre mora. La simulación sintética sigue siendo el entorno correcto para verificar la función de pago y el diseño de experimentos.

## Búsqueda de serie IDEAM fechada — 2026-11-11

Se identificaron dos vías oficiales que vale la pena distinguir:

| Vía | Evidencia y calidad declarada | Resultado para esta entrega |
|---|---|---|
| [Consulta y descarga DHIME](https://ideam.gov.co/dhime) | IDEAM describe herramientas de series temporales y acceso bajo demanda a datos oficiales. | La página es un portal de consulta/descarga, no un archivo de precipitación ya seleccionado para las coordenadas del companion. Se requiere seleccionar estaciones/periodo y conservar su exportación, metadatos y autorización de uso. |
| [Precipitación Nacional Diaria ZIP](https://www.ideam.gov.co/sites/default/files/transparencia/planeacion/respuesta_radicado_no_20249050054814_gsc.pdf) | En respuesta pública, IDEAM lista una descarga diaria nacional con disponibilidad desde la instalación de estaciones hasta el dato disponible. | El vínculo del ZIP `http://bart.ideam.gov.co/PQRS/AQTSUtils/PrecipitacionNacionalDiaria.zip` agotó tiempo de espera en esta sesión (30 s incluso fuera del sandbox); no se obtuvo archivo ni hash. Es un bloqueo de acceso de esta sesión, no evidencia de que la fuente haya sido retirada. |
| [Copia de Precipitaciones en Datos Abiertos](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Copia-de-Precipitaciones/ns63-ha4g) | El propio aviso indica que son lecturas crudas instantáneas de estaciones automáticas, no validadas por IDEAM, con posible retraso y errores; su uso no es evidencia jurídica. La metadata consultada identifica el recurso como visualización `chart`, sin columnas/tablas de serie consultables por la API. | No sirve como serie validada ni como backfill histórico para calibrar trigger o prima. Puede orientar una exploración de ingesta únicamente si se adquiere una exportación tabular documentada y se le aplica control de calidad. |

La descarga NASA POWER ya reproducida sigue siendo el único insumo meteorológico fechado incorporado. Para pasar a una comparación con observaciones de estación hay que obtener el ZIP oficial por una ruta accesible o exportar desde DHIME estaciones con cobertura espacial/temporal defendible, y después auditar grano, faltantes, cambios de estación, unidades y flags. Aun con precipitación IDEAM, exposición asegurada y daños/pagos siguen siendo necesarios para medir riesgo de base y validar un contrato.

## Actualización: catálogo IDEAM descargado (2026-11-11)

Se pudo descargar el [Catálogo Nacional de Estaciones IDEAM](https://www.datos.gov.co/d/hp9r-jxuu) del recurso oficial de datos abiertos. El companion [observed-ideam-station-catalog](observed-ideam-station-catalog/README.md) conserva el snapshot (SHA-256 `e377d9b8644ff2f1c720296d55a4534544f02a50eba88e45422c97d39de13095`) y una lista reproducible de cinco candidatas por cada una de las diez ciudades de NASA POWER. El endpoint devolvió 10.000 filas, con 132 duplicados exactos; la página institucional describe 9.685 estaciones. Por la discrepancia y el límite de consulta, no se interpreta el archivo como censo exhaustivo.

El catálogo eleva la preparación de selección de estaciones, pero **no cierra la brecha de observaciones**: el estado “Activa” y la proximidad a un centro urbano no acreditan lecturas diarias históricas, calidad, continuidad o representatividad de una zona asegurada. La mayoría de las candidatas más próximas aparecen activas, aunque cuatro de diez candidatas más cercanas figuran suspendidas. Sigue pendiente exportar las series históricas de estaciones elegidas desde [DHIME](https://www.ideam.gov.co/dhime), enlazarlas con coordenadas de exposición y conseguir resultados observados de daños/pagos.

## Nueva ruta identificada: API de precipitación (2026-11-11)

El [plan oficial de apertura de datos de IDEAM](https://www.ideam.gov.co/file-download/download/public/19626) enumera el dataset **Precipitación** con recurso `s54a-sgyg` en [Datos Abiertos](https://www.datos.gov.co/d/s54a-sgyg). El [manual institucional para consumir datos hidrometeorológicos](https://www.ideam.gov.co/sites/default/files/transparencia/datos-abiertos/2025-05/manual_consumo_de_datos.pdf) documenta el uso del API Socrata del portal y muestra el esquema de observaciones hidrometeorológicas; una consulta `limit=1` al endpoint oficial `https://www.datos.gov.co/resource/s54a-sgyg.json` respondió en esta sesión con un registro de precipitación, incluyendo código de estación/sensor, fecha-hora, valor, ubicación y unidad (mm). Se conservó temporalmente fuera del repositorio en `/private/tmp/ideam_precip_sample.json` (342 bytes; SHA-256 `bfb1ac83297bfeaf82a41aed84f11699226937bd0ea70611f593e989268bc759`). La fila de muestra es `SAN PEDRITO - TX GPRS`, Suan (Atlántico), sensor `0240`, fecha `2020-12-19 12:30`, valor `0 mm`; acredita el esquema y que el recurso entrega registros, no cobertura o continuidad de una estación candidata.

Las consultas focalizadas a la candidata Bogotá `2120000120` no devolvieron bytes antes del timeout: consulta API `where=codigoestacion='2120000120'`, `limit=1000`, orden ascendente por `fechaobservacion` (40 s); consulta equivalente con `limit=50000` (60 s). También agotó tiempo la consulta directa del servicio ArcGIS de DHIME `https://dhime.ideam.gov.co/server/rest/services/OSPA/Precipitacion/GPServer/Precipitacion?f=pjson` (30 s). La consulta de una fila al ZIP nacional histórico ya había agotado 30 s, según la sección anterior. Estos errores no prueban que el contenido haya sido retirado ni que las estaciones carezcan de datos.

Este recurso abierto es una pista concreta para continuar, pero aún no es una serie utilizable de los sitios asegurados: falta recuperar una ventana de estación candidata, comprobar disponibilidad temporal, duplicados, intervalos, faltantes, cambios de sensor y reglas de calidad, y contrastar su estatus con la descarga/validación DHIME. No se trasladan automáticamente a `s54a-sgyg` las advertencias de otra vista de datos crudos. Hasta conservar y auditar una consulta por estación con vintage y hash, NASA POWER sigue siendo el único archivo meteorológico analizado en el proyecto; incluso una serie IDEAM no validaría prima ni riesgo de base sin exposición y pérdidas/pagos.
