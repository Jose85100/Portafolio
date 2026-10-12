# Diseño matemático, operativo y de gobierno

## 1. Pregunta de decisión

Este modelo traduce una decisión de alta dirección en variables observables, restricciones explícitas y resultados verificables. La decisión final sigue correspondiendo a los órganos de gobierno.

## 2. Formulación

```text
Bonus = Salario·TargetRatio·Score·max(0,1−λ·LossRatio); pago actual=(1−d)·Bonus.
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

El score combina desempeño financiero y cliente. El diferimiento se registra, pero no existe todavía un calendario de vesting o clawback.

## 5. Validación y estrés

Brechas de compliance, riesgo excesivo, pesos y penalizaciones.

- Verificar casos de borde y consistencia aritmética.
- Comparar contra un caso manual independiente.
- Evaluar estabilidad ante perturbaciones de parámetros.
- Documentar explícitamente el origen y la fecha de cada dato antes de cualquier aplicación real.

## 6. Interpretación económica

El comité de remuneración puede comparar incentivos que premian crecimiento frente a desempeño sostenible.

## 7. Límites y riesgo de modelo

El modelo no resuelve formalmente el problema principal-agente ni estima esfuerzo oculto.

Los datos de ejemplo son sintéticos. No hay integración con ERP, core bancario, sistemas de nómina ni plataformas de M&A. La estimación empírica, el control de cambios, la autorización y la monitorización de desempeño quedan fuera de esta primera versión.

## 8. Reproducibilidad

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/13-executive-incentive-design/tests -v
```
