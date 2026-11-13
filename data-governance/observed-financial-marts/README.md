# Observed Financial Marts — SFC + Banco de la República

## Qué queda implementado

Pipeline sin dependencias externas para dos series observadas ya almacenadas en `Master_DATOS` de Google Drive. Consume **exportaciones locales autorizadas** (no agrega credenciales ni copia raw a GitHub), comprueba esquema, llaves, coherencia de observaciones, valores faltantes y construye:

- Stock de cartera sobre depósitos (cuenta corriente + ahorro + CDT).
- Crecimiento interanual nominal de cartera por mismo cierre trimestral.
- Proporción de cartera de vivienda.
- Tasas DTF e IBR del mes tres meses anterior al fin del trimestre, con alineamiento explícito.
- Correlación descriptiva (no causal) entre crecimiento de cartera y IBR rezagado.
- Archivos de resultados, hash de entradas y manifiesto de ejecución.

**Nota:** el archivo `sfc_agregado_nacional_mensual_desde_municipios.csv` está etiquetado como mensual, pero en los registros examinados contiene **82 cierres trimestrales** (2006-03-31 a 2026-06-30). No generar meses artificiales ni interpolaciones sin metodología. El archivo `banrep_tasas_mensuales.csv` contiene **514 meses** (1984-01 a 2026-10); IBR y TIB están ausentes en los primeros 288 y 291 meses, respectivamente. Los datos ausentes permanecen ausentes.

## Origen canónico

| Archivo de Drive | ID Drive | Validación exploratoria |
|---|---|---|
| `ATLAS_ECONOMICO_COLOMBIA/02_PROCESSED/sfc_agregado_nacional_mensual_desde_municipios.csv` | `1ufW5qhEN2Vvm5oNDYwmvv9L_NzY4YdWR` | 82 filas, 7 columnas, fecha única, cero celdas vacías |
| `ATLAS_ECONOMICO_COLOMBIA/02_PROCESSED/banrep_tasas_mensuales.csv` | `1Hpu_qk99U_-Hf0H3svT2GvVYWtb9EfpE` | 514 filas, 7 columnas, meses únicos, ausencia de IBR/TIB históricamente documentada |

No duplicar raw en Git. Drive retiene el activo canónico y el pipeline anota hash original y hash de salidas. Mantener permisos de lectura y validar licencia antes de redistribuir extractos.

## Ejecución reproducible

Descargar los dos CSV desde Drive a un directorio privado (fuera del repositorio). Ejemplo:

```bash
python3 data-governance/observed-financial-marts/src/financial_mart.py \
  --sfc /secure-data/sfc_agregado_nacional_mensual_desde_municipios.csv \
  --rates /secure-data/banrep_tasas_mensuales.csv \
  --out /secure-output/observed-marts
python3 -m unittest discover -s data-governance/observed-financial-marts/tests -v
```

Los modelos de `01-economics-and-econometrics`, `03-financial-risk` y `04-quant-strategy-and-products` podrán leer `observed_macro_credit_mart.csv` con validación de fuente, grano y fecha. **Aún no se han sustituido todos los generadores sintéticos ni actualizado cada notebook consumidor.**

## Evidencia exploratoria calculada con los CSV existentes de Drive

- 82 registros SFC, 514 mensuales BanRep.
- Último cierre SFC: 2026-06-30. Crecimiento interanual nominal de cartera: **9,1976%**.
- Ratio cartera/(cuenta corriente+ahorro+CDT) en último cierre: **0,98557**.
- 73 observaciones emparejadas de crecimiento interanual y tasa IBR del tercer mes previo.
- Correlación de Pearson descriptiva: **−0,19172**. No es inferencia causal, ni estabilidad de relación, ni modelo predictivo validado.
- Los resultados anteriores fueron calculados directamente sobre el contenido CSV accesible por Google Drive. No deben etiquetarse como ejecución del script Python nuevo hasta que el pipeline se corra efectivamente con esos mismos archivos.

## Precauciones financieras

- La serie SFC es agregada y potencialmente sujeta a modificaciones metodológicas, por lo que el ratio calculado no es un LDR regulatorio validado.
- Las tasas y los saldos pueden tener frecuencia y tiempos de publicación distintos; el rezago fijo no acredita disponibilidad as-known-at histórica.
- El modelo es descriptivo; no estima PD, LGD, EAD, SICR, riesgo de liquidez de una entidad ni una relación causal.
- Revisar períodos de observación, unidades monetarias, metodología SFC, revisiones, calidad de los cortes y fecha original de publicación.
- No usar estos cálculos como aprobación de underwriting, provisiones IFRS 9, recomendaciones de trading ni medición prudencial.

## Próximas conexiones

1. Feature store de series externas con `source_id`, `observation_date`, `published_at`, `retrieved_at`, `vintage`, `sha256`.
2. Conector autorizado de solo lectura a Drive con caché local y control de permisos; CI en GitHub solo valida el pipeline sin publicar raw.
3. Sensibilidades de cartera/depósitos al ciclo y curvas, con especificación de estacionariedad, factores omitidos, ventanas de estimación y backtesting OOT.
4. Incorporar el panel SFC por producto/mora y el panel bancario para stress; no inferir PD de saldos agregados.

## Investigación y fuentes pendientes

- [Notebook de diagnóstico con datos observados](notebooks/observed_macro_credit_diagnostics.ipynb) — carga exportaciones canónicas mediante variables de entorno, grafica el crecimiento y el ratio cartera/depósitos y mide correlación con tasas históricas. Requiere pandas y matplotlib y archivos autorizados; no incluye outputs precalculados.
- [Contratos de datos adicionales y brechas](DATA_GAPS.md) — objetivos de PD/LGD/EAD, escenarios, activos de mercado, pensiones, clima, economía regional y RAG, con fuentes y restricciones por grano.
- GitHub Actions realiza unit tests offline; los resultados empíricos exploratorios de este README provienen de la lectura efectiva de los CSV en Drive, no de una ejecución certificada del nuevo notebook.
