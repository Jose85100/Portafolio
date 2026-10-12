# Nota de diseño: 04-data-investment-prioritization

## Pregunta y criterio de decisión

El motor compara alternativas de decisión mediante un modelo explícito. Se diseñó para que sus supuestos puedan discutirse y las salidas puedan reproducirse con datos sintéticos antes de considerar una aplicación real.

## Formulación

```text
max Σ_i x_i(E[B_i]−C_i), sujeto a Σ_i C_i x_i≤presupuesto y x_i≤x_j si i depende de j.
```

## Arquitectura

```mermaid
flowchart LR
  A["Parámetros y escenarios"] --> B["Validación"]
  B --> C["Motor de decisión"]
  C --> D["Métricas y política"]
  D --> E["Pruebas de invariantes"]
```

La ejecución es local y no depende de servicios externos.

## Supuestos que importan

Búsqueda exhaustiva O(2^n) limitada a 22 iniciativas; costes enteros y beneficios aditivos; no modela complementariedades fuera de dependencias.

## Estrategia de validación

Comparar con enumeración manual en instancias pequeñas y revisar estabilidad ante escenarios.

El directorio `tests/` contiene pruebas de referencia, pero todavía no sustituye una campaña de sensibilidad, una validación empírica ni un análisis de rendimiento.

## Lectura económica y estratégica

La prioridad no depende únicamente del ROI; las dependencias técnicas y el presupuesto cambian la combinación óptima.

## Riesgos metodológicos

- Los parámetros se introducen manualmente; no existe una calibración a datos reales.
- Los resultados cambian si los escenarios o las probabilidades están mal especificados.
- No hay optimización multiobjetivo, evaluación de incertidumbre paramétrica ni análisis causal identificado.
- No hay integración productiva ni controles de autorización para decisiones de negocio.

## Reproducir

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/04-data-investment-prioritization/tests -v
```
