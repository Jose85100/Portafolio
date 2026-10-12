# Enterprise Risk Appetite & Board Reporting

## Decisión ejecutiva

Semáforo de apetito de riesgo, consumo de límites y escalamiento a comité.

El objetivo es que la salida sea útil para un comité de dirección: supuestos, alternativas, exposición al riesgo y una recomendación condicionada por límites verificables.

## Entregables

- [Motor Python](src/risk_appetite.py) con validación de entradas y resultados determinísticos.
- [Pruebas unitarias](tests/test_engine.py) para casos de referencia y condiciones adversas.
- [Nota técnica y diagrama](docs/DESIGN.md) con formulación, criterios de decisión y limitaciones.

## Ejecutar

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/08-enterprise-risk-appetite-board-reporting/tests -v
```

## Estado

Prototipo reproducible con datos sintéticos. No es un sistema de gobierno corporativo desplegado ni reemplaza la aprobación de directivos, junta o comité de riesgos.
