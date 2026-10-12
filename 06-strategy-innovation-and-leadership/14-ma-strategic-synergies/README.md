# M&A and Strategic Synergies

## Decisión ejecutiva

Valoración de adquisiciones por flujos incrementales, integración y escenarios.

Este producto convierte hipótesis de negocio en una decisión cuantificada y verificable. Se construye como un módulo autónomo para poder discutir resultados y supuestos sin depender de una plataforma externa.

## Componentes

- [Motor cuantitativo](src/ma_valuation.py) — validaciones y cálculo reproducible.
- [Pruebas](tests/test_engine.py) — escenarios normales, extremos y condiciones inválidas.
- [Diseño matemático](docs/DESIGN.md) — formulación, arquitectura, riesgos y criterios de decisión.
- [Caso de negocio](examples/CASE_STUDY.md) — supuestos, interpretación y discusión para comité.

## Ejecución

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/14-ma-strategic-synergies/tests -v
```

## Madurez

Implementación de referencia con datos sintéticos. No sustituye una política corporativa, una valoración independiente ni un informe regulatorio. No hay integraciones a sistemas empresariales.
