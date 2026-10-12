# Diseño matemático, operativo y de gobierno

## 1. Pregunta de decisión

Este modelo traduce una decisión de alta dirección en variables observables, restricciones explícitas y resultados verificables. La decisión final sigue correspondiendo a los órganos de gobierno.

## 2. Formulación

```text
max Σ_i x_i (Valor_i−Costo_i), sujeto a presupuesto, capacidad y dependencias x_i≤x_j.
```

## 3. Arquitectura

```mermaid
flowchart LR
  A["Hipótesis y datos"] --> B["Controles de entrada"]
  B --> C["Motor de escenarios"]
  C --> D["Métricas de decisión"]
  D --> E["Informe de comité"]
  E --> F["Revisión y aprobación humana"]
```

## 4. Supuestos y alcance

Modelo 0-1 exhaustivo; valores aditivos y personal asignado por iniciativa, sin calendarización multiperiodo.

## 5. Validación y estrés

Restricciones de recursos, precedencias y costos de oportunidad.

- Verificar casos de borde y consistencia aritmética.
- Comparar contra un caso manual independiente.
- Evaluar estabilidad ante perturbaciones de parámetros.
- Documentar explícitamente el origen y la fecha de cada dato antes de cualquier aplicación real.

## 6. Interpretación económica

CEO/COO: seleccionar una cartera de transformación ejecutable, no solo una lista ordenada por ROI.

## 7. Límites y riesgo de modelo

La complejidad crece exponencialmente y no se modelan riesgos de adopción ni interdependencias económicas.

Los datos de ejemplo son sintéticos. No hay integración con ERP, core bancario, sistemas de nómina ni plataformas de M&A. La estimación empírica, el control de cambios, la autorización y la monitorización de desempeño quedan fuera de esta primera versión.

## 8. Reproducibilidad

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/15-enterprise-transformation-portfolio/tests -v
```
