# Labor Productivity & Growth Accounting

Un equipo directivo que evalúa automatización necesita separar una narrativa sobre tecnología de la productividad que efectivamente se observa en la economía. Este proyecto mantiene un laboratorio controlado para estudiar mecanismos de crecimiento y añade una serie observada de PIB por persona empleada en Colombia. En WDI, esa medida creció a una tasa compuesta de 1,32% anual entre 1991 y 2025; su crecimiento compuesto fue 1,93% en 2010–2019 y 1,21% en 2020–2025. Es una descripción de producción por trabajador, no una medida de productividad total de factores ni evidencia del impacto causal de IA. Sirve para contextualizar hipótesis de productividad y delimitar qué datos de firma, horas, capital y adopción se necesitan para atribuir efectos.

## Dos ediciones

### Laboratorio controlado

El [notebook reproducible](notebooks/01-estimation-and-robustness.ipynb) conserva mecanismos explícitos y escenarios controlados para estudiar identificación, sensibilidad y error de medición.

### Aplicación observada

- [Informe de resultados, lectura y límites](reports/official-application-2026-11-10.md)
- [Datos WDI y transformaciones](data/README.md)
- [Runner reproducible](official_application.py)
- [Resumen versionado](data/official/application_summary.json)
- [Serie anual derivada](data/official/annual_productivity.csv)

Reproducción desde este directorio, con Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

## Pregunta de investigación
Crecimiento y productividad. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
Delta ln Y = alpha Delta ln K + (1-alpha) Delta ln L + Delta ln A
\]

## Estrategia econométrica
Descomposición y error de medición. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Datos y trazabilidad
La aplicación observada usa WDI `SL.GDP.PCAP.EM.KD`, PIB por persona empleada en dólares internacionales constantes de 2021, cobertura anual 1991–2025. El indicador es una estimación del Banco Mundial basada en fuentes externas documentadas. Consulta hashes, definición, vintage y transformaciones en [data/README.md](data/README.md). No se interpreta como productividad total de factores.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Impacto de IA en productividad.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Sustituye el ejemplo OLS genérico anterior; las cantidades siguen siendo sintéticas y no elevan el proyecto a validación empírica.

La aplicación observada es independiente: resume la evolución realizada de una medida de productividad laboral y no valida los parámetros del laboratorio ni atribuye cambios a tecnología, inversión o política.
