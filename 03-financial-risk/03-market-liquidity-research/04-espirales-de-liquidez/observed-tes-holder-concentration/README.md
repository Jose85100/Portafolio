# Concentración observada de tenedores TES

## Pregunta y uso

¿Cómo cambia la concentración de las tenencias TES entre las categorías de tenedor que publica la fuente oficial? Este companion transforma el laboratorio controlado de concentración en una lectura descriptiva de la base inversora agregada. Puede orientar el monitoreo y ayudar a especificar datos necesarios para estudios de liquidación; no demuestra que los tenedores vendan juntos ni mide liquidez de mercado.

## Definición

Para cada mes, con tenencias (V_{g,t}) de categoría publicada (g) y total (V_t), se calcula:

```text
s[g,t] = V[g,t] / V[t]
HHI[t] = 10,000 × Σ_g s[g,t]²
Top3[t] = 100 × suma de las tres mayores participaciones
```

El grano es categoría de tenedor × mes. Los importes están expresados en millones de COP. El universo es el que cubre el archivo; las categorías no representan entidades individuales ni beneficiarios finales.

## Fuente y gobierno

La fuente es el [Histórico Evolución de Tenedores TES 2010–2025 del portal IRC](https://www.irc.gov.co/deuda-publica/deuda-interna-gnc/tenedores-tes/2025/-/document_library/dpfm/view_file/3002586). El insumo canónico archivado es `irc_tenedores_tes_historico.xlsx`, en `Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/01_RAW/02_datos_crudos/`. Se consume desde su ubicación canónica o desde un staging temporal verificado; **no se duplica el XLSX crudo en este producto**.

- ID Drive: `1VXxopmjxSdZf6JJxpZA6BFd0uiWXsnff`
- Hoja: `Diciembre2025`; cobertura mensual enero de 2010–diciembre de 2025.
- Vintage/última modificación del archivo en Drive: 2026-10-08 17:13:12 UTC.
- Unidad indicada por la fuente: millones de pesos.
- SHA-256 esperado: `a900a98916e3dd8fd9242b4f776953201ead023b4ca3621d729e6247dc47a2ce`.
- La fuente suma 21 categorías por corte; el runner verifica fechas únicas y ordenadas, campos numéricos y no negativos, total positivo y conciliación de categorías con el total (tolerancia relativa (10^{-10})). Un cambio de vintage requiere revisar y actualizar explícitamente el hash, periodo y resultados.

## Resultado

La lectura de resultados, figura y manifiesto versionados se genera en `results/` y `figures/`. El HHI es un indicador descriptivo de concentración entre categorías amplias. Una categoría puede contener actores muy distintos y la métrica puede ocultar concentración al interior de una categoría; asimismo, cambios de clasificación o cobertura afectan su comparabilidad.

## Trade-off, límites y decisión admisible

Se eligió el HHI de participaciones publicadas por categoría porque es reproducible con la fuente disponible y no requiere inventar posiciones individuales. Esto sacrifica resolución: no equivale al HHI entre tenedores finales, ni a concentración de ventas o de exposición negociable. El valor de tenencias tampoco informa la fracción libre de gravámenes o disponible para vender.

El companion no observa cotizaciones, bid-ask, libro de órdenes, volúmenes transados, operaciones de venta, compromisos de margen ni impacto de precio. No estima profundidad, `λ`, pérdida por venta forzada, ES dinámico o contagio. La lectura admisible es descriptiva y sirve para priorizar solicitudes de datos y vigilancia de composición. La calibración de fire-sale requiere posiciones por tenedor × emisión × fecha, tenencia disponible vs. comprometida, transacciones con precio/cantidad/fecha y medidas de mercado con suficiente frecuencia alrededor de episodios de estrés.

## Reproducción

Requiere Python 3 con `openpyxl` y `matplotlib`:

```bash
python3 scripts/build_companion.py --source /ruta/al/canonico/irc_tenedores_tes_historico.xlsx
```

El runner verifica el hash fijado, deriva el CSV mensual, el manifiesto, el informe y la figura. Para staging se copia el archivo canónico a una ubicación temporal y se proporciona esa ruta; el producto no debe almacenar el archivo crudo.

## Artefactos

- [Resultados y límites](results/report.md)
- [CSV mensual derivado](results/tes_holder_concentration_monthly.csv)
- [Manifiesto de vintage, hash y conciliaciones](results/manifest.json)
- [Concentración mensual](figures/tes_holder_concentration.png)
