# CEED: proxy de área paralizada/inactiva en construcción residencial

**Edición complementaria observada** del laboratorio de riesgo de cronograma y sobrecostos. El proxy usa el área en estado paralizado o inactivo publicada por DANE sobre el área total censada en proyectos residenciales. Es una señal sectorial de composición de obras al corte; no mide demoras contractuales, pérdidas ni desempeño de una constructora.

## Definición y decisión admisible

```text
Proxy de área paralizada (%) = 100 × área paralizada/inactiva / área total censada
```

Se calcula para apartamentos, casas y vivienda conjunta. Para vivienda conjunta se suman los metros cuadrados de apartamentos y casas antes de dividir; no se promedian sus porcentajes. El indicador puede orientar una revisión de exposición sectorial a obra detenida, priorizar escenarios de vigilancia y aportar un benchmark contextual al monitoreo de proyectos. No debe tratarse como tasa de incumplimiento, probabilidad de atraso o severidad de pérdida.

## Resultado y artefactos

- [Informe con corte más reciente, fórmula y límites](results/official_report.md)
- [Datos por trimestre y destino](results/ceed_stage_share_by_quarter.csv)
- [Manifiesto de fuente, cobertura, calidad y hash](results/manifest.json)
- [Figura del proxy](figures/paused_inactive_area_share.png)

## Fuente y calidad

Fuente primaria: [DANE, Censo de Edificaciones (CEED), históricos](https://www.dane.gov.co/index.php/comunicados-y-boletines/construccion-y-vivienda/censo-de-edificaciones). Se congela el [anexo Estructura general por estados de obra y destino, II trimestre de 2026](https://www.dane.gov.co/files/operaciones/CEED/anex-CEED-EstructuraSeriesDestino-IItrim2026.xlsx). Hoja `Serie 20 áreas (57_mpios)`, área en metros cuadrados.

- Cobertura de esa hoja: agregado de 14 áreas urbanas, cinco metropolitanas y Cundinamarca. No identifica empresa, proyecto o crédito individual.
- Ventana seleccionada: 2015-T4 a 2026-T2, 43 cortes trimestrales por destino y 86 filas destino-trimestre.
- Estados usados: total de área censada y total de área paralizada/inactiva. El CSV también presenta área total en proceso para dar contexto.
- En la ventana seleccionada no se encontraron claves duplicadas, áreas negativas ni valores de área vacíos. No se imputan datos.
- Los cortes de 2026 caen dentro del plazo de provisionalidad de un año que DANE señala; están sujetos a revisión.

## Trade-offs y gobierno

Se usa el agregado de 57 municipios y se limita el análisis a apartamentos y casas para definir una base residencial consistente y reproducible. Se conserva la clasificación que publica DANE en lugar de redefinir “obra detenida”. El denominador es el área total censada del mismo destino y trimestre: evita comparar solo conteos de obras, pero hace que el ratio sea sensible a la composición de tamaños de proyecto.

La etiqueta “paralizada/inactiva” es de la operación estadística y no equivale a incumplimiento de un plazo contractual. Entran y salen obras del universo censado, y puede variar la cobertura o el estado reportado. La medida no captura tiempo detenido, causa, costo pendiente, ventas, deuda, avance financiero, recuperación ni pérdida. No permite inferir causalidad ni trasladar la señal agregada a un prestatario o proyecto particular.

Para validar un modelo de sobrecostos o atrasos se requieren IDs de proyectos, presupuestos fechados y cambios de alcance, cronogramas planificados y reales, órdenes y facturas, hitos, financiación, preventas y resultados finales. Esos datos deben permitir validación fuera de tiempo, análisis por cohortes y revisión independiente. El CEED ofrece un contraste sectorial; no calibra ni valida el motor del laboratorio.

## Reproducción

Desde esta carpeta, ejecutar:

```bash
python3 scripts/build_companion.py
```

Requiere Python y los paquetes listados en `requirements.txt` (`pip install -r requirements.txt`). El runner solo lee el snapshot congelado y regenera CSV, informe, manifiesto y figura.
