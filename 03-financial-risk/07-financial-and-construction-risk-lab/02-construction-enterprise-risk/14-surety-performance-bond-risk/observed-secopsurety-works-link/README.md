# Garantías SECOP II y contratos de obra: enlace administrativo

Una entidad que supervisa contratos de obra necesita conocer qué registros de garantías pueden asociarse a sus contratos. Esta aplicación enlaza registros públicos de SECOP II por `id_contrato` y describe la cobertura y composición administrativa del enlace. La coincidencia entre registros ayuda a explorar calidad de datos; por sí sola no establece cobertura jurídica ni riesgo de pérdida.

## Fuentes y alcance

Se consultan contratos SECOP II ([jbjy-vk9h](https://www.datos.gov.co/resource/jbjy-vk9h.json), seleccionando `tipo_de_contrato=Obra`) y garantías ([gjp9-cutm](https://www.datos.gov.co/resource/gjp9-cutm.json)). El cruce usa IDs de contrato en memoria; las salidas no guardan IDs ni filas originales. En la extracción del **11 de noviembre de 2026**, se recibieron 50.154 IDs únicos de contratos de obra y 48.949 filas de garantías de todos los tipos. De estas, 4.584 filas coincidieron con 1.076 contratos de obra. El indicador de 2,15 % es una proporción de coincidencia entre estos conjuntos en ese corte, no cobertura de garantía de todas las obras.

El [resumen](results/summary.json) incluye los conteos y límites; el [manifiesto](results/manifest.json) documenta la fecha y hashes de entradas y salidas; la [tabla](results/linked_rows_by_status_subtype.csv) y la [figura](results/linked_guarantee_rows_by_status.png) muestran la distribución administrativa. Los conjuntos cambian con el tiempo y no se conserva un snapshot completo; una nueva descarga puede dar resultados distintos. Los hashes de páginas permiten identificar el contenido de la extracción, no reconstruirlo si la fuente cambia.

## Reproducir

Desde esta carpeta, con Python y acceso a internet:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build_companion.py
```

El script consulta los endpoints, compara los conteos recibidos con los publicados y genera resultados agregados y manifiesto en `results/`. Revisar las condiciones de uso de datos abiertos de las fuentes antes de redistribuirlas o usarlas en otra aplicación.

## Limitaciones y decisión de diseño

Se escogió un enlace administrativo y conteos agregados porque las fuentes consultadas no aportan una clave de póliza/versionado para deduplicar garantías, ni resultados enlazados de reclamaciones, pagos o recuperaciones. Existen varios tipos, estados y posibles revisiones por contrato. Un estado aceptado no prueba vigencia o suficiencia jurídica. No se estiman probabilidad de ejecución, severidad, pérdida ni desempeño del contratista. Para validar esas magnitudes se requiere el historial de pólizas, obligaciones, reclamaciones y pagos, con conciliación y revisión independiente; véase la [brecha de datos](../DATA_GAP.md).
