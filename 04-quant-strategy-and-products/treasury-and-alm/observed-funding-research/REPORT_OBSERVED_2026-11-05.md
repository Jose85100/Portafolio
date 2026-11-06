# ALM empírico: fondeo agregado colombiano y escenarios de retiro

**Fecha de análisis:** 2026-11-05. **Fuente:** `Master_DATOS/ATLAS_ECONOMICO_COLOMBIA/02_PROCESSED/sfc_agregado_nacional_mensual_desde_municipios.csv`; Drive ID `1ufW5qhEN2Vvm5oNDYwmvv9L_NzY4YdWR`. El nombre dice mensual, pero 82 filas son trimestrales. El archivo original sigue en Drive; no se publica raw en Git.

## Resultados de ejecución local sobre datos reales

- **82 trimestres** desde 2006-03-31 hasta 2026-06-30, 81 variaciones QoQ.
- Fuente SHA-256: `21f2557be07b97899f7b507ea9ae81e7d8e5abb6b644d590fdceeb1384ff88e5`.
- Último saldo observado de depósitos seleccionados (cuentas corrientes + ahorro + CDT): **COP 2.021.346.769.991.592**.
- Última cartera agregada: **COP 1.992.184.027.344.505,50**.
- Cartera / depósitos seleccionados: **0,9855726**.
- Composición de depósitos: CDT **44,1508 %**, ahorro **46,8752 %**, corriente **8,9740 %**.
- Crecimiento QoQ del saldo de depósitos seleccionados en último trimestre: **2,0951 %**.
- Cuantiles históricos de crecimiento QoQ de los depósitos seleccionados: **p05 = −0,0226 %**, **p50 = 2,3922 %**, **p95 = 7,0029 %**. Son cuantiles descriptivos sin ajuste por inflación, estacionalidad, cambios de composición ni cambios de reporte.

## Escenarios de runoff **hipotéticos**, no estimados

Se calculan manteniendo constante el saldo de cartera; las tasas de retiro son elecciones experimentales, no mediciones históricas de depositantes ni parámetros aprobados.

| Escenario | Corriente: retiro supuesto | Ahorro: retiro supuesto | CDT: retiro supuesto | Retiro efectivo agregado | Cartera / fondeo remanente |
|---|---:|---:|---:|---:|---:|
| Base observado | 0 % | 0 % | 0 % | 0 % | 98,557 % |
| Moderado | 5 % | 3 % | 2 % | 2,738 % | 101,332 % |
| Severo | 15 % | 12 % | 8 % | 10,503 % | 110,124 % |
| Extremo | 30 % | 25 % | 18 % | 22,358 % | 126,938 % |

**Interpretación:** no representan LCR, NSFR, brecha contractual por vencimientos, liquidez disponible, liquidez contingente, shock IFRS 9, ni probabilidades de pérdida. El denominador excluye categorías de pasivos distintas a las tres mencionadas; el numerador agrupa cartera sin incorporar realización de activos, amortizaciones o recuperación.

## Reproducibilidad

```bash
python 04-quant-strategy-and-products/treasury-and-alm/observed-funding-research/src/observed_alm.py \
  --sfc /private/drive/sfc_agregado_nacional_mensual_desde_municipios.csv \
  --out /private/derived-alm
```

Produce `observed_funding_quarters.csv` (derivado) y `observed_alm_report.json` con SHA del original, SHA del derivado, cobertura, cuantiles y escenarios. Cinco tests locales se ejecutaron con éxito antes de publicar el módulo; el estado de GitHub Actions se verifica por separado.

## Próximas variables para extender el modelo

1. Integrar tasas BanRep IBR/DTF por disponibilidad histórica y vintage para comparar costo marginal, preservando que DTF no representa tasas pagadas a todos los depósitos.
2. Añadir productos y entidades SFC después de resolver colisiones y jerarquía de renglones.
3. Obtener escalera de vencimientos, concentración de depósitos, tasas efectivas contractuales, buffer de HQLA y comportamiento de retiros con licencia, para un ALM bancario y liquidez de nivel institución.
4. Estimar escenarios condicionados a regímenes macro y validar contra periodos de estrés reales, sin etiquetar las reglas hipotéticas como predictivas.
