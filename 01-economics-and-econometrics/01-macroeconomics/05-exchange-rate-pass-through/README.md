# Exchange Rate Pass-Through: laboratorio y aplicación observada

Una empresa que importa insumos necesita saber si los movimientos cambiarios coinciden con cambios en los precios al consumidor y cuánto tarda esa relación. Este proyecto conserva un laboratorio controlado para estudiar la regresión distribuida y añade una aplicación mensual con IPC empalmado de DANE y TRM diaria de BanRep. En 272 observaciones de mayo de 2003 a diciembre de 2025, la suma descriptiva de la respuesta contemporánea y tres rezagos es 0,016 puntos porcentuales por punto de devaluación, con IC HAC de 95% [-0,015; 0,047], tras incluir efectos estacionales y tendencia lineal. La evidencia no muestra una asociación estadísticamente distinguible de cero bajo esta especificación. No identifica causalidad ni descarta pass-through a precios transables, rubros particulares o plazos distintos; señala que el IPC agregado mensual y la TRM de referencia no bastan para una regla de precios.

## Dos ediciones

### Laboratorio controlado

El [notebook reproducible](notebooks/01-estimation-and-robustness.ipynb) conserva un proceso generador conocido, OLS, validación temporal, bootstrap y sensibilidad para observar la dinámica del estimador bajo supuestos controlados.

### Aplicación observada con datos oficiales

- [Informe de resultados, decisiones y límites](reports/official-application-2026-11-10.md)
- [Datos DANE/BanRep congelados y transformaciones](data/README.md)
- [Runner reproducible](official_application.py)
- [Resumen de coeficientes HAC](data/official/application_summary.json)
- [Panel mensual](data/official/monthly_panel.csv)

Para reproducir desde este directorio, con NumPy, statsmodels, openpyxl y Matplotlib:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

## Pregunta de investigación
Traslado de devaluación a inflación. ¿Bajo qué supuestos puede identificarse el mecanismo y qué magnitud tendría su efecto?

## Ecuación de referencia
\[
Delta p_t = alpha + sum_j beta_j Delta e_(t-j) + eps_t
\]

## Estrategia econométrica
Regresión distribuida y colinealidad. Definir unidad de observación, muestra, identificación, variables de control, errores estándar y alternativas. Comparar modelos parsimoniosos y estructurales; reportar incertidumbre y falsaciones.

## Resultado y límite de aplicación

La regresión mensual usa la variación logarítmica del índice IPC empalmado y de la TRM mensual promedio, con 3 rezagos cambiarios, efectos de mes, tendencia lineal y errores HAC(6). La suma contemporánea y rezagada es 0,016 (IC 95% [-0,015; 0,047]); al omitir la tendencia es 0,020 (IC 95% [-0,015; 0,055]). Los datos permiten comprobar que el flujo de transformación y la regresión funcionan con series observadas, pero no validan un coeficiente estructural. La muestra acaba en diciembre de 2025, aunque la serie DANE llega a octubre de 2026.

## Notebook
[Laboratorio reproducible](notebooks/01-estimation-and-robustness.ipynb): DGP sintético, OLS baseline, validación fuera de muestra, bootstrap y perturbación de ruido. **La ecuación económica es el objetivo de investigación; el notebook todavía no estima el modelo estructural completo.**

## Validación y entregables
- Test de identidades económicas y rangos de parámetros.
- Validación temporal, estabilidad, sensibilidad y benchmark.
- Discusión de endogeneidad, cambios de régimen y validez externa.
- Nota ejecutiva: Costos tecnológicos y precios de pagos.


## Desarrollo estructural de la revisión semanal

El [notebook](notebooks/01-estimation-and-robustness.ipynb) desarrolla el mecanismo específico de este proyecto, con DGP o equilibrio explícito, supuestos de identificación, 40 réplicas por escenario cuando corresponde, sensibilidad, oráculos y límites. Las cantidades de ese laboratorio siguen siendo sintéticas; el companion observacional es una estimación aparte y no prueba el mecanismo causal.

El laboratorio controlado verifica propiedades bajo un proceso generador explícito; la aplicación mensual resume una relación publicada y declara por qué no identifica causalidad. Ambas ediciones responden preguntas distintas y sus conclusiones no se mezclan.
