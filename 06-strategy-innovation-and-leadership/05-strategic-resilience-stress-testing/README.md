# Strategic Resilience & Stress Testing

## Decisión que aborda

Traducir choques macroeconómicos y operativos a liquidez, runway y umbrales de supervivencia.

## Método

Simulación de escenarios, trayectorias de caja y probabilidad de ruptura de covenant.

## Alcance de esta versión

Motor reproducible en Python estándar, sin dependencias externas ni conexiones a datos privados. Incluye pruebas unitarias y escenarios sintéticos. Las estimaciones son condicionales a los supuestos: no constituyen asesoría de inversión ni una decisión empresarial validada.

## Estructura

- [`resilience.py`](src/resilience.py): implementación y validación de entradas.
- [`tests/test_engine.py`](tests/test_engine.py): casos de referencia e invariantes.
- [`docs/DESIGN.md`](docs/DESIGN.md): derivación, diagrama, supuestos y límites.

## Ejecutar

Desde la raíz del repositorio:

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/05-strategic-resilience-stress-testing/tests -p 'test_*.py' -v
```

## Integración temática

**Área:** strategy. Este producto es independiente de los ejercicios históricos en `strategy/` y evita reemplazar o renombrar sus notebooks.
