# Corporate Strategic Planning & Scenario Engine

## Decisión ejecutiva

Planeación corporativa de tres estados simplificados, crecimiento, margen, capex y caja.

Este producto convierte hipótesis de negocio en una decisión cuantificada y verificable. Se construye como un módulo autónomo para poder discutir resultados y supuestos sin depender de una plataforma externa.

## Componentes

- [Motor cuantitativo](src/strategic_plan.py) — validaciones y cálculo reproducible.
- [Pruebas](tests/test_engine.py) — escenarios normales, extremos y condiciones inválidas.
- [Diseño matemático](docs/DESIGN.md) — formulación, arquitectura, riesgos y criterios de decisión.
- [Caso de negocio](examples/CASE_STUDY.md) — supuestos, interpretación y discusión para comité.

## Ejecución

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/11-corporate-strategic-planning/tests -v
```

## Madurez

Implementación de referencia con datos sintéticos. No sustituye una política corporativa, una valoración independiente ni un informe regulatorio. No hay integraciones a sistemas empresariales.
