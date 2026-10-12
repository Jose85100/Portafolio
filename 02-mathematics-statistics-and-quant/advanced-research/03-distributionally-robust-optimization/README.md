# Distributionally Robust Optimization

> **Madurez: S1 — protocolo de investigación.** No se afirma código, experimentos ejecutados, revisión sistemática concluida ni novedad demostrada.

## Pregunta de investigación

¿Cómo calibrar conjuntos de ambigüedad que mejoren decisiones fuera de muestra bajo no estacionariedad?

## Hipótesis contrastable

El método propuesto supera a baselines explícitos en al menos una métrica predefinida, sin degradación inaceptable en robustez, calibración ni costo. Esta hipótesis debe operacionalizarse antes de observar resultados.

## Formulación matemática

min_{x∈X} sup_{Q:W_p(Q,P̂)≤ε} E_Q[ℓ(x,ξ)]; dualidad convexa y sensibilidad al radio ε.

**Trabajo teórico pendiente:** definir espacios de probabilidad y parámetros, supuestos de existencia e identificabilidad, resultados de convergencia o estabilidad, demostraciones y contraejemplos. No se presume que tales propiedades estén establecidas.

## Modelado estadístico y estimación

Comparar ERM, robust optimization y Wasserstein DRO con radios por concentración y validación.

Estimar sesgo, varianza, consistencia bajo supuestos adecuados e intervalos de incertidumbre. Separar evaluación predictiva de identificación causal.

## Métodos numéricos y protocolo experimental

Contaminación, colas pesadas, covariate shift y cambio estructural; medir regret, cobertura y costo computacional.

**Diseño mínimo:** (1) generador sintético con verdad conocida; (2) baseline trivial y avanzado; (3) evaluación fuera de muestra o por réplicas independientes; (4) ablaciones y pruebas adversariales; (5) tiempos, memoria y sensibilidad a hiperparámetros; (6) semillas, versiones y resultados reproducibles.

## Aplicación económico-financiera

Capital, liquidez, asignación de portafolios.

## Limitaciones y posibles fallos

Garantías dependen de soporte, dimensión, regularidad de la pérdida y elección del radio.

## Entregables y criterios de aceptación

- **S1:** revisión bibliográfica verificable, hipótesis operacionales, teoremas/proposiciones y plan preregistrado de simulación.
- **S2:** módulos `src/`, `tests/`, datos sintéticos y script de reproducción, con cobertura de invariantes y casos límite.
- **S3:** comparadores estadísticos, tablas y figuras generadas, análisis de sensibilidad, errores numéricos y benchmark de recursos.
- **S4:** réplica independiente, aplicación con datos públicos licenciados, documentación de riesgos y límites de validez.

## Estructura prevista (no creada aún)

```text
theory/       # supuestos, derivaciones y pruebas
src/          # modelos, estimadores y algoritmos
tests/        # tests unitarios y estadísticos
experiments/  # simulaciones y benchmarks
data/         # manifiestos y fuentes públicas
docs/         # interpretación, limitaciones y referencias
```

**Regla de evidencia:** no reportar métricas, resultados, referencias bibliográficas ni garantías matemáticas que no hayan sido verificadas.
