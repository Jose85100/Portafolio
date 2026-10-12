# Market Entry & Strategic Games

## Decisión que aborda

Modelar entrada competitiva, reacción de incumbentes y equilibrio estratégico en un juego simultáneo.

## Método

Equilibrios de Nash puros y mixtos para juegos 2x2; análisis de sensibilidad y dominancia.

## Alcance de esta versión

Motor reproducible en Python estándar, sin dependencias externas ni conexiones a datos privados. Incluye pruebas unitarias y escenarios sintéticos. Las estimaciones son condicionales a los supuestos: no constituyen asesoría de inversión ni una decisión empresarial validada.

## Estructura

- [`market_entry.py`](src/market_entry.py): implementación y validación de entradas.
- [`tests/test_engine.py`](tests/test_engine.py): casos de referencia e invariantes.
- [`docs/DESIGN.md`](docs/DESIGN.md): derivación, diagrama, supuestos y límites.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/02-market-entry-game-theory/tests -p 'test_*.py' -v
```

## Integración temática

**Área:** strategy. Este producto es independiente de los ejercicios históricos en `strategy/` y evita reemplazar o renombrar sus notebooks.
