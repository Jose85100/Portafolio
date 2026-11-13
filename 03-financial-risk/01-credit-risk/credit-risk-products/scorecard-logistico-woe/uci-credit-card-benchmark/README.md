# Benchmark externo UCI para scorecard — pendiente de snapshot

## Estado de disponibilidad

Se auditó el proyecto scorecard porque su pregunta requiere una etiqueta de incumplimiento a nivel cliente. El panel SFC `rvii-eis8` ya disponible en Drive es agregado por entidad/producto/mes; no contiene ID de cliente, originación ni resultado individual. Reutilizarlo para AUC, calibración o cosechas sería inválido. Las búsquedas en Drive por nombre de archivo UCI, `default_of_credit_card_clients`, `UCI_Credit_Card.csv` y variantes de `credit_card_clients.xls` no encontraron el dataset.

El mejor candidato abierto es **Default of Credit Card Clients** de UCI, dataset 350, con 30.000 registros, 23 variables y resultado de incumplimiento del siguiente mes. Puede servir como benchmark externo del pipeline de scorecard, nunca como validación de una población colombiana. La página UCI describe una muestra de clientes de tarjeta en Taiwán con historia mensual entre abril y septiembre de 2005 y licencia CC BY 4.0. Referencia: Yeh, I.-C. (2009), [DOI 10.24432/C55S3H](https://doi.org/10.24432/C55S3H), [registro y archivos del repositorio UCI](https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients). OpenML también indexa la publicación/dataset bajo el [ID 42477](https://www.openml.org/search?id=42477&sort=runs&type=data), pero no se obtuvo el contenido desde ese host.

**No se generó snapshot local, SHA-256, modelo ni métrica.** El endpoint UCI de descarga del ZIP respondió por la herramienta web con error de tamaño superior a 4 MiB. `curl` al endpoint oficial y a una ruta de descarga OpenML falló antes de la descarga con `Could not resolve host`; el fetch web de ambas rutas de descarga no acepta el archivo. Se inspeccionaron Drive y staging local sin encontrar el snapshot. No se sustituye con una copia de terceros ni con el laboratorio sintético.

## Endpoints primarios a reintentar

```text
ZIP actual: https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip
Excel legado: https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls
API / ficha: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
```

Reintento verificable fuera de este entorno, conservando el raw fuera del repo:

```bash
mkdir -p /private/tmp/uci-350
curl -fLsS 'https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip' -o /private/tmp/uci-350/source.zip
shasum -a 256 /private/tmp/uci-350/source.zip
unzip -l /private/tmp/uci-350/source.zip
```

Tras obtener el archivo desde el host oficial, guárdelo fuera de Git (o en un staging local gobernado), calcule SHA-256 del archivo y de su extracción, lea la hoja de datos con control de encabezados y tipos, y registre fecha de recuperación, tamaño, nombres de columnas y clase. No se debe publicar el raw en el portafolio sin revisar los términos de redistribución del artefacto descargado.

## Diseño de evaluación propuesto

1. Conservar el objetivo fuente `default payment next month` como etiqueta binaria, sin llamarlo PD de 12 meses ni default IFRS 9.
2. Aplicar el scorecard WoE/logístico a variables disponibles en el corte de observación. Inspeccionar el diccionario oficial para confirmar el significado temporal de estados de pago y excluir cualquier campo que revele información posterior al corte.
3. Separar entrenamiento y prueba con semilla fija y estratificación, documentar que la base no trae una fecha individual que permita holdout temporal. Reportar prevalencia, AUC, KS, Brier/calibración y matriz de confusión a umbral declarado; incluir intervalo/variación por remuestreo si el tamaño lo permite.
4. Mantener `ID` solo como llave de auditoría, no como predictor. Reportar resultados por grupos protegidos/descriptivos como diagnóstico, con cautela por el contexto y la edad de la muestra.
5. Marcar todo resultado como **benchmark académico extranjero de 2005**. No usarlo para aprobar crédito, inferir performance en Colombia, calibrar provisiones o declarar equidad regulatoria.

## Bloqueo y brecha

Para completar el benchmark se requiere una de estas condiciones: que el host UCI sea resoluble desde el entorno de ejecución, que se entregue una exportación local del archivo obtenido de UCI con procedencia verificable, o que el mismo snapshot esté accesible en Drive. El SHA del archivo aún no existe; cuando se disponga, debe agregarse aquí antes de publicar cualquier resultado. La fuente SFC agregada ya usada en companions anteriores no reemplaza esta necesidad de etiquetas individuales.

### Intento de recuperación oficial por CLI (2026-11-11)

Se reintentó el ZIP canónico enlazado por la ficha UCI, sin pasar por repositorios de terceros:

```bash
curl -fLsS 'https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip' -o /private/tmp/uci-350-official.zip
```

Resultado del entorno: `curl: (6) Could not resolve host: archive.ics.uci.edu` (código de salida 6). La descarga asistida desde el enlace oficial de la ficha también fue rechazada porque el contenido supera el límite de lectura de 4 MiB de la herramienta web; el archivo UCI indicado es de 5,3 MB. El endpoint oficial de metadatos `https://archive.ics.uci.edu/api/dataset?id=350` no fue accesible por la herramienta web. La solicitud de ejecutar el `curl` fuera del sandbox fue interrumpida antes de descargar datos. Por tanto, no hay respuesta HTTP ni bytes locales que permitan comprobar tamaño descargado, SHA-256, esquema o licencia del artefacto; la ficha sí declara 30.000 observaciones, 23 variables y licencia CC BY 4.0. Se detuvieron los intentos sin usar espejos ni sustituir la etiqueta con datos agregados.

## Auditoría de alternativa: South German Credit (2026-11-11)

Se revisó también [South German Credit, UCI dataset 573](https://archive.ics.uci.edu/dataset/573/south+german+credit), que sería un benchmark extranjero compatible con scorecard: 1.000 préstamos históricos y una etiqueta binaria, no una muestra colombiana. El archivo canónico ZIP de UCI no se pudo recuperar desde este entorno. Un conector pudo leer [`data/SouthGermanCredit.asc` del repositorio público `iancovert/sage`](https://github.com/iancovert/sage/blob/master/data/SouthGermanCredit.asc); el contenido tiene 1.000 filas de datos y 21 columnas y el identificador Git blob reportado es `9d809301a941c6d17f4cd2da1626c0fe621a7973`. **Ese identificador acredita el blob del espejo, no su identidad con el archivo oficial de UCI.** No se incorporó el archivo, no se calculó un modelo ni se reportó ninguna métrica.

La alternativa queda descartada por ahora por falta de procedencia íntegra desde UCI. Para desbloquearla se necesita el ZIP canónico descargado de UCI —o una exportación preservada con cadena de custodia y checksum oficial verificable— y una conciliación de bytes o, si el formato cambia, de esquema, filas, distribución de clases y código de datos. Sin eso no se puede llamar al espejo snapshot oficial reproducible. Aun al desbloquearse, el resultado solo sería benchmark histórico extranjero; no validaría PD colombiana, originación ni ECL.
