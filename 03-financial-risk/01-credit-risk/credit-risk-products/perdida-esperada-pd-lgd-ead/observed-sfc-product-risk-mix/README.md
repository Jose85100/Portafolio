# Mezcla agregada de calificación de riesgo por producto — SFC

Companion observada para explorar cómo cambia la distribución de saldos reportados en categorías D/E dentro de cada producto financiero. Conserva el laboratorio de pérdida esperada sintético como ejercicio metodológico; este análisis aporta contexto real de cartera agregada, pero **no valida PD, LGD, EAD ni pérdida esperada**.

## Pregunta y uso admisible

¿Qué proporción del saldo clasificado en A–E se encuentra en D o E por producto y corte mensual, y qué parte del saldo bruto está cubierta por esas calificaciones? El resultado puede apoyar vigilancia sectorial y orientar preguntas de análisis. No es una medida de default individual ni una predicción.

La serie se calcula después de sumar saldos entre entidades reportantes:

\[
\text{Participación D+E}_{p,t}=100\times\frac{D_{p,t}+E_{p,t}}{A_{p,t}+B_{p,t}+C_{p,t}+D_{p,t}+E_{p,t}}
\]

El denominador es **saldo calificado A–E**, no saldo bruto. El campo `cobertura_calificacion_sobre_bruto_pct` muestra por separado:

\[
\text{Cobertura A–E}_{p,t}=100\times\frac{A_{p,t}+B_{p,t}+C_{p,t}+D_{p,t}+E_{p,t}}{\text{saldo bruto}_{p,t}}.
\]

El CSV conserva también saldos A–E, saldo bruto, número de entidades reportantes y filas fuente. No se calcula una probabilidad sobre cuentas ni se asignan pesos/umbrales de decisión.

## Fuente, vintage y grano

- **Fuente oficial:** Superintendencia Financiera de Colombia, [Distribución de cartera por producto (rvii-eis8)](https://www.datos.gov.co/en/en/Public-Finance/Distribuci-n-de-cartera-por-producto/rvii-eis8); [API pública](https://www.datos.gov.co/resource/rvii-eis8.csv?$limit=200000) y [metadata](https://www.datos.gov.co/api/views/rvii-eis8.json).
- **Linaje canónico Drive:** `Master_DATOS/04_SHADOW_RISK/01_RAW/01_RAW/2026-10-02_respaldo_local_pesados/docs/macro_2026_data/sfc_datasets/rvii-eis8.csv.gz`, Drive file ID `1FcdcUTlIHhV92TN8pEikcz0DX0896HBW`. Los datos crudos no se copian aquí; este proyecto conserva un derivado agregado reproducible.
- **Vintage de este snapshot:** descarga API observada el 10-nov-2026; metadata del Socrata indicaba última actualización 23-oct-2026 y el corte más reciente de datos es agosto de 2026. El hash del archivo realmente procesado se encuentra en [`results/manifest.json`](results/manifest.json).
- **Grano fuente:** entidad reportante × fecha de corte × código de modalidad/producto × renglón de reporte.
- **Grano derivado:** fecha de corte × código de producto (`unicap`); suma de saldos por entidad.
- **Filtro:** `renglon = 5`, renglón de total del producto. Se excluyen los renglones de subproductos para evitar doble conteo.
- **Calificaciones usadas:** los saldos A, B, C, D y E son columnas `_18`, `_20`, `_22`, `_24` y `_26` de la fuente. Se excluyen las alturas de mora: esos campos no son necesarios para esta medida y algunos tramos se superponen.
- Se conservan las unidades originales de saldo sin conversión. Las proporciones no dependen de la unidad; antes de interpretar montos, revise el diccionario oficial aplicable al vintage.

## Comparabilidad, calidad y trade-offs

La comparación principal es **temporal dentro de cada producto**. No se recomienda ordenar modalidades por esta tasa: composición de deudores, escala de calificación, regulación, cobertura y prácticas de reporte pueden diferir. El agregado también cambia cuando cambian las entidades reportantes o sus participaciones; la cifra no controla esos efectos.

La validación de integridad incluye esquema requerido, fechas convertibles, saldos numéricos, llave única entidad×corte×producto×renglón, unicidad del producto-mes derivado y SHA-256 del raw exacto utilizado. El `manifest.json` informa nulos, duplicados, filas de saldo bruto cero, cobertura A–E y fechas. El ID y path del archivo canónico de Drive quedan registrados; el acceso disponible no permitió comparar byte a byte ese gzip archivado contra la descarga pública, por lo que el hash **no** afirma esa equivalencia. Para reproducir exactamente este snapshot, use el CSV de entrada que tenga ese hash.

La figura presenta cuatro productos cuya cobertura A–E mínima histórica en este vintage es al menos 95%; el eje secundario muestra cobertura en cada fecha. Esa selección facilita lectura, pero no arregla diferencias entre productos ni reemplaza la inspección de los 32 productos del CSV.

## Resultado y decisión que habilita

El [informe reproducible](results/official_report.md) presenta el corte más reciente, comparación interanual por producto y controles de cobertura. La [figura](figures/sfc_product_risk_grade_mix_selected_products.png) permite detectar movimientos de composición D/E para decidir **dónde profundizar el análisis con datos institucionales de créditos y reglas de rating comparables**. Una variación no identifica su causa ni predice pérdidas.

## Límites de aplicación y validación pendiente

El dataset es un corte agregado, no un panel de cuentas. No contiene IDs estables de crédito/deudor ni el seguimiento individual entre meses. Por tanto, no identifica entradas, curas, migraciones A→E, default contractual ni roll-rates. Tampoco valida una PD de originación, modelo de pérdida esperada, LGD, EAD, suficiencia de provisiones, causalidad, discriminación o calibración.

Para validar esos usos se necesitarían datos institucionales gobernados con IDs seudonimizados persistentes, fechas de originación y observación, saldo/exposición, eventos y definición aprobada de default, mora, cura y castigo; política de rating por versión y producto; outcomes observados en un horizonte definido; y una muestra temporal fuera de desarrollo para validación independiente. Ninguna salida de este companion habilita originación, precio, límites, provisiones o decisiones adversas.

## Reproducción

Requisitos: Python 3.10+, `pandas` y `matplotlib` (ver [`requirements.txt`](requirements.txt)). Desde esta carpeta:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_companion.py --input /ruta/local/rvii-eis8.csv
```

El modo anterior es offline y usa el CSV local exacto. Para actualizar desde la fuente oficial, omita `--input`; el script descarga el CSV actual usando `curl` y el endpoint público (se requiere red y `curl`). Cada actualización crea un nuevo hash/vintage en el manifiesto y puede reemplazar los artefactos derivados; archive los resultados si necesita preservar vintages anteriores. El pipeline no descarga desde Drive ni requiere credenciales.

```text
data/processed/sfc_product_risk_grade_mix_monthly.csv
results/manifest.json
results/official_report.md
figures/sfc_product_risk_grade_mix_selected_products.png
```
