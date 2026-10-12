# Diseño técnico y lectura ejecutiva

## Modelo de decisión

```text
Progreso_i=clip((Actual_i−Base_i)/(Objetivo_i−Base_i),0,1); avance=Σw_i Progreso_i/Σw_i.
```

## Diagrama

```mermaid
flowchart LR
 A["Hipótesis de negocio"] --> B["Parámetros y límites"]
 B --> C["Validación de datos"]
 C --> D["Motor cuantitativo"]
 D --> E["Indicadores de decisión"]
 E --> F["Revisión de comité"]
```

El último paso es una revisión humana, no una aprobación automática.

## Supuestos

Los OKR se miden en una misma fecha, los pesos son positivos y los objetivos son comparables por su escala normalizada.

## Controles y pruebas

Pruebas de objetivos crecientes/decrecientes, saturación y metas inconsistentes.

## Aplicación ejecutiva

CEO/COO: revisar avance, responsables y objetivos que requieren intervención.

## Riesgos de interpretación

Los datos son sintéticos y no están calibrados a una empresa. No existe conexión con ERP, core bancario, CRM ni sistemas de gobierno. La utilidad de una política requiere estimación, validación y responsabilidad institucional. La optimización matemática no sustituye la discusión de restricciones legales, regulatorias y reputacionales.

## Reproducir

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/07-executive-strategy-okr-operating-system/tests -v
```
