# Escalera hipotética escalada a un corte SFC observado

Este ejercicio conecta la [escalera de caja](../../engines/liquidity_ladder.py) con **dos variables observadas agregadas**, no con vencimientos reales. Para los bancos en agosto de 2026, la SFC reporta activos líquidos de mercado (ALM) de **160.953.536 millones de COP** y requerimiento de liquidez neto a 30 días (RLN) de **90.040.630 millones de COP**; su cociente es 178,7566 %. Ambas cifras son componentes agregados publicados, no caja y salidas realizadas de una entidad. La escala de salida del motor es COP, no millones de COP.

## Fuente, alcance y trazabilidad

- Fuente primaria: [SFC, Resultados del sistema financiero colombiano agosto de 2026](https://www.superfinanciera.gov.co/publicaciones/10116287/resultados-del-sistema-financiero-colombiano-agosto-de-2026/), tabla 12, página 20 del PDF; fecha de modificación de la página 16 de octubre de 2026.
- [PDF congelado](../../../03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/data/raw/sfc_resultados_sistema_financiero_2026-08.pdf), SHA-256 `e38b879140f70d523b655af2aa72c12531f802473604d99bddc15fc57f8b985d`.
- [CSV derivado y documentado](../../../03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/results/sfc_irl_bulletin_appendix.csv) por el [companion SFC existente](../../../03-market-liquidity-research/03-liquidez-estocastica/observed-sfc-irl/README.md). SHA-256 del CSV `eb9282570324306fb3a8509307a95d707df6721d0717439307525473f1615146`.
- Grano: un corte × tipo de entidad; no son observaciones por banco. El boletín indica que las cifras están sujetas a revisión. Se trata de una vintage congelada, no de una conexión actualizada ni un panel diario. El acceso es público; condiciones de reutilización no verificadas, atribuir a SFC y consultar términos antes de redistribución externa.

## Variables y supuestos construidos

| Variable | Construcción | Naturaleza y límites |
|---|---|---|
| ALM | Componente bancario de agosto, millones COP × 1.000.000 | Observado agregado; no es efectivo ni garantiza disponibilidad inmediata. |
| RLN 30 días | Componente bancario de agosto, millones COP × 1.000.000 | Requerimiento regulatorio neto agregado, no representa salidas brutas ni fechas de pago observadas. |
| Caja inicial | 60 % del ALM observado | Fracción hipotética arbitraria que representa liquidez utilizable; no es haircut estimado ni colateral efectivamente disponible. |
| Salidas totales | RLN × 1, 1,5 y 2 en base, adverso y severo | Escala hipotética, sin calibración ni probabilidad. RLN no se convierte empíricamente en retiros observados. |
| Vencimientos | Tres partes iguales a 10, 20 y 30 días | Fechas y montos ficticios; se distribuyen centavos residuales para cuadrar exactamente el total. No se incluyen ingresos ni financiación. |

Los escenarios se sitúan ilustrativamente entre el 1 de noviembre y el 1 de diciembre de 2026, después de la fecha de modificación de la página fuente. No se reconstruye una vintage informacional completa ni se afirma que estos escenarios se realizaron. Las cifras en [results.json](results.json) son determinísticas, en COP y con identificadores ficticios.

| Escenario | Multiplicador | Saldo final, millones COP | Primera fecha con saldo negativo |
|---|---:|---:|---|
| Base | 1,0 | 6.531.491,6 | Ninguna |
| Adverso | 1,5 | −38.488.823,4 | 2026-12-01 |
| Severo | 2,0 | −83.509.138,4 | 2026-11-21 |

Estos resultados describen solo las reglas hipotéticas. La combinación de promedios/componentes regulatorios agregados con un calendario arbitrario **no reconstruye flujos reales**, no valida un SARL, no estima la probabilidad de iliquidez y no calcula nuevamente el IRL de una entidad ni establece cumplimiento. Cambiar el calendario o la fracción utilizable cambia el resultado. La falta de ingresos y fondeo es un supuesto restrictivo. Las salidas de un sector tampoco pueden sumarse a una posición de un banco individual.

## Sensibilidad conjunta

La [matriz reproducible](sensitivity_results.json) cruza fracciones utilizables hipotéticas de ALM de 40%, 60% y 80% con salidas de 1, 1,5 y 2 veces el RLN. Para cada combinación informa primera fecha negativa, saldo de cierre y financiación inicial mínima para evitar saldos negativos de cierre, sin interés ni costos. Bajo los supuestos del escenario severo (60% y 2 veces), esa financiación es COP 83.509.138,4 millones. Es una propiedad aritmética de los supuestos y el corte, no un requerimiento real ni una medida de pérdidas. La matriz no asigna probabilidades ni estima liquidez intradía. Las pruebas también comprueban que el faltante no disminuye al incrementar salidas y no aumenta al subir la fracción utilizable, manteniendo los demás supuestos fijos.

## Reproducción y pruebas

Desde la raíz del repositorio, con Python estándar:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/08-regulatory-risk-systems/04-sarl-liquidity/observed-sfc-proxy/run.py
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/08-regulatory-risk-systems/04-sarl-liquidity/observed-sfc-proxy/sensitivity.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/08-regulatory-risk-systems/04-sarl-liquidity/observed-sfc-proxy -v
```

Los runners necesitan el CSV, el PDF congelado y el motor existentes del repositorio; no hacen descargas. Ambos rechazan los archivos si sus hashes no coinciden con los documentados, evitando reutilizar el resultado con otro vintage. Las pruebas verifican unidades, conciliación, sensibilidad de escenarios y rechazo de cortes ausentes/duplicados y supuestos inválidos. Los hashes identifican los archivos usados; no prueban por sí solos que la extracción corresponda a la fuente. Para reconstruir el CSV desde el PDF véase el companion, que documenta su conciliación con la figura publicada.
