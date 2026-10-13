# Arquitectura

```mermaid
flowchart LR
  Q[Consulta] --> R{Política}
  R -->|siempre| M1[Un nivel]
  R -->|cascada| C[Pequeño → confianza ≥ λ?]
  C -->|sí| A[Respuesta]
  C -->|no| L[Grande]
  R -->|aprendido| F[Atributos → p(acierto)]
  F --> M1
  F --> L
  K[(Caché semántico)] -.-> R
  CAL[Calibración<br/>control conforme] --> C
  B[Bandido en línea] -.-> R
  O[Asignación bajo presupuesto<br/>Lagrange + cota LP] -.-> R
```

## Decisiones de diseño

- Resultados de los niveles correlacionados y sorteados una sola vez por consulta: todas las políticas se comparan sobre las mismas realizaciones.
- El umbral de la cascada se calibra con **control conforme del riesgo** (corrección de muestra finita), no a ojo.
- La pérdida de calidad se define frente al modelo grande: 1[pequeño acepta, falla y grande acierta].
- La asignación usa relajación de Lagrange y se verifica contra `linprog`.

## Límites

- Todo es simulado: habilidades, costos y confianzas son supuestos.
- El control conforme supone intercambiabilidad calibración–producción; con deriva se pierde la garantía.
- Los bandidos no usan contexto; el caché usa embeddings sintéticos.
