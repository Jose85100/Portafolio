# Sovereign Yield Spreads

El costo nominal de emitir deuda local a largo plazo resume varias fuerzas al mismo tiempo. Este proyecto conserva su laboratorio controlado de primas de riesgo y agrega una medida observada de rendimientos TES en pesos colombianos frente a Treasury de EE. UU. a 10 años. La medida es un **proxy de diferencial nominal**, no una estimación de prima soberana: también recoge inflación esperada, depreciación, política monetaria, liquidez y primas por plazo. Su uso admisible es monitorear condiciones relativas y alimentar escenarios de sensibilidad, no inferir riesgo de default o decidir una inversión.

## Aplicación observada: proxy nominal de 10 años

- [Informe de lectura, sesgos y límites](reports/official-proxy-2026-11-10.md)
- [Datos, definiciones y hashes](data/README.md)
- [Runner reproducible](official_proxy.py)
- [Resumen de cobertura y estadísticas](data/official-proxy/proxy_summary.json)
- [Panel mensual](data/official-proxy/monthly_yield_differential.csv)

Reproducción desde esta carpeta, con Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_proxy.py
```

## Pregunta de investigación
Prima de riesgo soberano. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
spread_t=alpha+beta debt_t+gamma risk_t+eps_t
\]

## Estrategia econométrica
Cointegración y rupturas estructurales. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
La aplicación usa curvas mensuales de TES cero cupón 10 años COP de BanRep y rendimientos diarios Treasury a 10 años USD, promediados por mes. El diferencial nominal entre monedas es un proxy con limitaciones económicas claras; fechas, unidad, fórmula y hashes están en [data/README.md](data/README.md).

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Costo de fondeo.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.

El companion observado no estima la ecuación deuda–prima ni valida el riesgo soberano estructural. Demuestra la construcción y límites de un indicador proxy con series de mercado observadas.
