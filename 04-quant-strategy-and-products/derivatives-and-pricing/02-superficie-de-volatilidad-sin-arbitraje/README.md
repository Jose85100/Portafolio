# Superficie de volatilidad sin arbitraje

**Estado: idea de investigación.** Esta carpeta organiza la propuesta existente; no afirma implementación, datos, resultados ni validación.

## Propuesta

- Ajustar sonrisas y superficies en strikes y vencimientos imponiendo consistencia de precios, convexidad y restricciones de calendar spread.
- Comparar SVI parametrizado con splines penalizados; reportar dónde los datos no identifican la superficie.

## Contraste propuesto

**Referencia:** Ajuste de smile sin restricciones globales.

**Enfoque planteado:** Superficie con restricciones de no arbitraje incorporadas durante calibración.

**Evaluación propuesta:** Evaluar error de precio y contar violaciones de butterfly/calendar antes y después en cotizaciones reservadas.

**Prueba decisiva:** pendiente de definir con hipótesis falsable, datos, métrica y criterio de aceptación.

[Volver al área](../README.md) · [Metodología común](../../METODOLOGIA_BASE_E_INNOVACION.md)

La [captura de opciones observadas](observed_options/README.md) aporta cotizaciones para investigar esta idea; no constituye una superficie calibrada.
