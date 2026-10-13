# Arquitectura

```mermaid
flowchart LR
  S[Fuente<br/>duplicados · desorden · correcciones] --> V{Contrato<br/>validación}
  V -->|inválido| Q[(Cuarentena)]
  V -->|válido| B[(Bronce<br/>append-only)]
  B --> U[Upsert idempotente<br/>gana (event_time, batch_id, huella)]
  U --> SV[(Plata)]
  SV --> G[Oro incremental<br/>solo fechas afectadas]
  G --> R[Conciliación<br/>huella de contenido]
  SV --> D[SCD tipo 2]
  W[Marca de agua] -.-> U
```

## Decisiones de diseño

- Un lote se aplica **una sola vez** (`batch_id`) y **todo o nada** (transacción).
- La versión vigente de un evento la decide `(event_time, batch_id, huella)`, no el orden de llegada.
- La llave primaria no se valida por lote en un flujo con correcciones (error encontrado y corregido).
- El oro se recalcula solo para las fechas afectadas y se contrasta con una reconstrucción completa.
- La compatibilidad de contratos usa una tabla de reglas suficiente (correcta) contrastada con fuerza bruta.

## Límites

- SQLite no escala a producción; el diseño ilustra las propiedades, no un lakehouse.
- Un solo escritor a la vez (sin concurrencia).
- El monitor estadístico se probó con un solo defecto semántico (cambio de escala).
