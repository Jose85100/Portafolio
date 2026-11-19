# Caso reproducible: tablero de apetito y escalamiento

Prototipo de investigación en Python estándar. Evalúa tres indicadores sintéticos en escenarios base, adverso y severo, produce un reporte de comité y conserva observaciones faltantes como `SIN DATO`. No realiza predicción, optimización, consolidación de unidades ni atribuye cumplimiento normativo. Las cifras, límites, responsables y acciones son hipotéticos, sin aprobación institucional.

## Ejecutar desde la raíz del repositorio

```bash
python3 03-financial-risk/05-enterprise-risk-advisory/01-erm-governance/risk-appetite/case/appetite.py
python3 -m unittest discover -s 03-financial-risk/05-enterprise-risk-advisory/01-erm-governance/risk-appetite/case -p 'test_*.py' -v
```

Se pueden pasar `--config ruta.json` y `--observations ruta.csv`. El programa escribe el reporte en stdout y falla ante entradas inválidas; no guarda ni modifica los insumos. En el ejemplo, el escenario severo carece de concentración deliberadamente, para mostrar que una ausencia no equivale a cumplimiento.

## Contrato y decisión

`config.json` define escenarios y, por métrica, identificador único, etiqueta, unidad, dirección, rango de entrada, umbrales, responsable y acción sugerida. El máximo de 10.000 % para liquidez es un límite de calidad ilustrativo, no un máximo financiero. `observations.csv` requiere `scenario,metric_id,value,unit`; una fila representa un indicador de un escenario, para una misma fecha y perímetro. Los valores son números finitos, sin símbolo de porcentaje; la unidad debe coincidir exactamente. Se rechazan escenarios o métricas desconocidos, duplicados, unidades incompatibles, valores fuera de rango y umbrales mal ordenados. Los indicadores configurados sin fila se muestran como `SIN DATO`; una fila con valor vacío es error de calidad.

Las tres razones se expresan en puntos porcentuales: mora = cartera vencida / cartera bruta × 100; liquidez = activos líquidos / salidas netas a 30 días × 100; concentración = exposición de la mayor contraparte / exposición total × 100. Los denominadores deben ser estrictamente positivos y ambos términos corresponder al mismo perímetro y corte. **El prototipo recibe razones ya calculadas y no comprueba esos denominadores ni calcula un indicador regulatorio.**

Para límites superiores, valores iguales o superiores al límite son `BRECHA`, y valores iguales o superiores a alerta pero menores al límite son `ALERTA`; para límites inferiores se invierten las desigualdades. El resto es `NORMAL`. Los escenarios son valores hipotéticos suministrados, no shocks estimados ni pronósticos. Las acciones son sugerencias estáticas para revisión, no decisiones automáticas ni prueba de ejecución del control.

Antes de un uso real se necesitan contratos de extracción con fecha de corte y disponibilidad, conciliación de numeradores y denominadores, perímetro, trazabilidad, límites y responsables aprobados, tratamiento de excepciones, seguimiento de remediación, controles de acceso y validación independiente. El cálculo de escalamiento y una cascada consistente por unidades siguen pendientes.

## Ejercicio con base observada SFC y escenarios hipotéticos

[Ver el reporte reproducido con el snapshot versionado](observed_sfc_report.md).

`observed_sfc.py` integra dos históricos SFC ya conservados en el repositorio. Filtra por clave de entidad y fecha, exige exactamente una fila en cada fuente y no usa nombres como llave. La base es **entidad bancaria tipo 1 código 1, Banco de Bogotá, diciembre de 2022**, identificada como `1-1` en IRL y `entity_type_code=1, entity_code=1` en ICV; las fuentes usan nombres con grafías distintas. No representa su situación actual ni una decisión de su comité.

| Métrica del ejercicio | Fuente y variable | Grano y alcance | Interpretación |
|---|---|---|---|
| ICV de consumo | [Calidad de cartera SFC](https://www.superfinanciera.gov.co/publicaciones/10082252/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualcalidad-de-cartera-establecimientos-de-credito-10082252/), campo `icv_reported_pct` | Entidad × modalidad × mes; corte 2022-12 | Proxy de cartera y leasing de consumo vencidos/brutos; no es mora total, PD ni vintage. |
| IRL 30 días | [Indicador de liquidez SFC](https://www.superfinanciera.gov.co/publicaciones/10108220/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-de-riesgo-de-liquidez-indicador-de-riesgo-de-liquidez-irl-10108220/), campo `irl_pct_reported` | Entidad × mes; promedios de la fuente a 30 días; corte 2022-12 | Ratio reportado de activos líquidos y requerimiento neto, no probabilidad de escasez ni caja individual. |
| Concentración de contraparte | Sin fuente identificada | No disponible | Se mantiene `SIN DATO`; no se estima a partir del ICV o IRL. |

Se reutilizan los CSV transformados de [ICV](../../../../01-credit-risk/credit-risk-products/observed-sfc-quality-proxy/README.md) e [IRL](../../../../03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/README.md), con hashes SHA-256 `333144bae0eeae4713137a65a7126e7f39e2fe0bcf89337b366dda464e0c2fa8` y `d4b1e8eb6bb1606abd9c5f0fed572d00a19d2cd5a4da94d83eb4b5bb1c801929`, respectivamente. Los snapshots brutos y sus hashes, metodología, vacíos y controles se documentan en esos enlaces. Ambos fueron descargados en 2026-11-10; son históricos, no una descarga reciente ni *vintages* disponibles en el momento de decisión en 2022.

La base conserva el valor reportado; el escenario adverso suma **1,5 puntos porcentuales** al ICV y resta **20 puntos porcentuales** al IRL, y el severo suma **3 pp** y resta **50 pp**, respectivamente. Son perturbaciones inventadas para probar el tablero: no se estiman de la distribución histórica, no son pronósticos ni probabilidades. Los umbrales del archivo de ejemplo son arbitrarios, no los límites de la entidad ni una prueba de cumplimiento. El IRL promedio mensual y el ICV de fin de mes tienen ventanas de medición distintas; el corte común es útil para demostración, no demuestra simultaneidad intradía.

Desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/05-enterprise-risk-advisory/01-erm-governance/risk-appetite/case/observed_sfc.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/05-enterprise-risk-advisory/01-erm-governance/risk-appetite/case -p 'test_*.py' -v
```

El runner calcula el hash de ambos CSV al ejecutar y falla si la clave seleccionada falta o está duplicada; el evaluador valida valores finitos, rangos, unidades y umbrales. En el extracto SFC de ICV se omiten observaciones faltantes y no se dispone de numerador y denominador separados para este ratio; no es posible reconciliar el valor de la modalidad con cartera total. Para aplicar esto en una entidad se requieren fecha de disponibilidad, perímetro, datos contables y de flujos, conciliación de numeradores y denominadores, límites aprobados y validación independiente.


## Seguimiento mensual histórico de indicadores

[historical_sfc.py](historical_sfc.py) integra la serie mensual de la misma entidad y modalidad entre marzo de 2020 y diciembre de 2022, y [guarda el resultado](historical_sfc_results.csv). Las 34 fechas tienen ambos ratios en este snapshot. Se usa el calendario completo de cierres mensuales, llave de entidad y período exactos, y se rechazan duplicados. Un mes sin observación queda `SIN DATO`, sin arrastrar ni interpolar valores; interrumpe el conteo de meses consecutivos por encima o debajo del límite hipotético, pero no prueba una recuperación. El indicador de concentración siempre queda `SIN DATO`.

El seguimiento aplica retroactivamente los umbrales **ilustrativos actuales del ejemplo**, no límites históricos de la entidad: 25 meses de alerta y 9 de brecha para ICV; 24 normales y 10 alertas para IRL. La secuencia máxima de brechas de ICV es nueve meses; IRL no registra ninguna con estos umbrales. Son clasificaciones de un ejercicio retrospectivo, no evaluación de cumplimiento ni alertas emitidas en tiempo real. No se conocen las fechas originales de disponibilidad del snapshot, y el IRL promedio mensual y el ICV de cierre no tienen idéntico momento de medición.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/05-enterprise-risk-advisory/01-erm-governance/risk-appetite/case/historical_sfc.py
```

La salida CSV va a stdout y los hashes de los dos insumos a stderr; para regenerar el archivo basta redirigir stdout a `historical_sfc_results.csv`. Las pruebas incluyen controles de continuidad, duplicados, faltantes y reproducción.
