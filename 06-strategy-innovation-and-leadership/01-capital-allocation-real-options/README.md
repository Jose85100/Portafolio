# Capital Allocation & Real Options

## Decisión que aborda

Decidir entre invertir ahora, esperar o abandonar cuando la incertidumbre y la irreversibilidad importan.

## Método

Opciones reales y programación dinámica; el valor de esperar surge de la decisión óptima, no de descontar flujos medios.

## Alcance de esta versión

Motor reproducible en Python estándar, sin dependencias externas ni conexiones a datos privados. Incluye pruebas unitarias y escenarios sintéticos. Las estimaciones son condicionales a los supuestos: no constituyen asesoría de inversión ni una decisión empresarial validada.

## Estructura

- [`capital_allocation.py`](src/capital_allocation.py): implementación y validación de entradas.
- [`tests/test_engine.py`](tests/test_engine.py): casos de referencia e invariantes.
- [`docs/DESIGN.md`](docs/DESIGN.md): derivación, diagrama, supuestos y límites.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/01-capital-allocation-real-options/tests -p 'test_*.py' -v
```

## Integración temática

**Área:** strategy. Este producto es independiente de los ejercicios históricos en `strategy/` y evita reemplazar o renombrar sus notebooks.
