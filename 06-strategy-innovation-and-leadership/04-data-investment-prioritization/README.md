# Data Investment Prioritization

## Decisión que aborda

Elegir iniciativas de datos y automatización bajo presupuesto, dependencias y beneficios inciertos.

## Método

Optimización exacta 0-1 tipo knapsack con precedencias y valoración de escenarios.

## Alcance de esta versión

Motor reproducible en Python estándar, sin dependencias externas ni conexiones a datos privados. Incluye pruebas unitarias y escenarios sintéticos. Las estimaciones son condicionales a los supuestos: no constituyen asesoría de inversión ni una decisión empresarial validada.

## Estructura

- [`investment_prioritization.py`](src/investment_prioritization.py): implementación y validación de entradas.
- [`tests/test_engine.py`](tests/test_engine.py): casos de referencia e invariantes.
- [`docs/DESIGN.md`](docs/DESIGN.md): derivación, diagrama, supuestos y límites.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/04-data-investment-prioritization/tests -p 'test_*.py' -v
```

## Integración temática

**Área:** data-leadership. Este producto es independiente de los ejercicios históricos en `data-leadership/` y evita reemplazar o renombrar sus notebooks.
