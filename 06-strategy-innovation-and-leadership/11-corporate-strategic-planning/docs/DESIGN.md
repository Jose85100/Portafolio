# Diseño matemático, operativo y de gobierno

## 1. Pregunta de decisión

Este modelo traduce una decisión de alta dirección en variables observables, restricciones explícitas y resultados verificables. La decisión final sigue correspondiendo a los órganos de gobierno.

## 2. Formulación

```text
FCF_t = EBIT_t − impuestos_t − CAPEX_t − ΔNWC_t; Caja_t = Caja_{t−1}+FCF_t.
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

La planeación utiliza ingresos iniciales, crecimiento, márgenes, capex y capital de trabajo; no incorpora deuda, intereses, depreciación ni financiación.

## 5. Validación y estrés

Escenarios de recesión, inflación de costos y crecimiento acelerado.

- Verificar casos de borde y consistencia aritmética.
- Comparar contra un caso manual independiente.
- Evaluar estabilidad ante perturbaciones de parámetros.
- Documentar explícitamente el origen y la fecha de cada dato antes de cualquier aplicación real.

## 6. Interpretación económica

La junta puede comparar caja terminal y liquidez bajo hipótesis alternativas.

## 7. Límites y riesgo de modelo

El tratamiento simplificado de impuestos y CAPEX no equivale a un estado de flujos de efectivo NIIF.

Los datos de ejemplo son sintéticos. No hay integración con ERP, core bancario, sistemas de nómina ni plataformas de M&A. La estimación empírica, el control de cambios, la autorización y la monitorización de desempeño quedan fuera de esta primera versión.

## 8. Reproducibilidad

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/11-corporate-strategic-planning/tests -v
```
