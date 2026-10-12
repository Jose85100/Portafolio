# Executive Strategy & OKR Operating System

## Decisión ejecutiva

Tablero ejecutivo de objetivos, avance ponderado, alertas y responsables.

El objetivo es que la salida sea útil para un comité de dirección: supuestos, alternativas, exposición al riesgo y una recomendación condicionada por límites verificables.

## Entregables

- [Motor Python](src/okr.py) con validación de entradas y resultados determinísticos.
- [Pruebas unitarias](tests/test_engine.py) para casos de referencia y condiciones adversas.
- [Nota técnica y diagrama](docs/DESIGN.md) con formulación, criterios de decisión y limitaciones.

## Ejecutar

```bash
python3 -m unittest discover -s 06-strategy-innovation-and-leadership/07-executive-strategy-okr-operating-system/tests -v
```

## Estado

Prototipo reproducible con datos sintéticos. No es un sistema de gobierno corporativo desplegado ni reemplaza la aprobación de directivos, junta o comité de riesgos.
