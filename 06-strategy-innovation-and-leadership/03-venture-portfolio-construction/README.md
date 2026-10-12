# Venture Portfolio Construction

## Decisión que aborda

Evaluar diversificación de startups, capital por ticket y distribución asimétrica de retornos.

## Método

Monte Carlo con retornos correlacionados, probabilidad de pérdida y expected shortfall.

## Alcance de esta versión

Motor reproducible en Python estándar, sin dependencias externas ni conexiones a datos privados. Incluye pruebas unitarias y escenarios sintéticos. Las estimaciones son condicionales a los supuestos: no constituyen asesoría de inversión ni una decisión empresarial validada.

## Estructura

- [`venture_portfolio.py`](src/venture_portfolio.py): implementación y validación de entradas.
- [`tests/test_engine.py`](tests/test_engine.py): casos de referencia e invariantes.
- [`docs/DESIGN.md`](docs/DESIGN.md): derivación, diagrama, supuestos y límites.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/03-venture-portfolio-construction/tests -p 'test_*.py' -v
```

## Integración temática

**Área:** venture-capital. Este producto es independiente de los ejercicios históricos en `venture-capital/` y evita reemplazar o renombrar sus notebooks.
