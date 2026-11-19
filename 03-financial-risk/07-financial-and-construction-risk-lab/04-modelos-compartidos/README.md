# Modelos compartidos de riesgo financiero y construcción

Este laboratorio reúne los componentes utilizados por varios temas: simulación de caja y cronograma, indicadores de deuda y pérdidas de cartera. Los diseños y aplicaciones específicas están en las carpetas corporativa y de construcción del [laboratorio principal](../).

- [Notebook integrado](notebook.ipynb): caja, cronograma, DSCR y pérdidas.
- `python/`: modelos y pruebas.
- `cpp/`: motor y pruebas C++17.
- `tests/fixtures/`: datos de referencia compartidos para pruebas de cola.

Los ejemplos del motor son simulaciones, no validación con datos de una empresa. Para comandos y alcance de cada modelo, consulta el [catálogo](../MODEL_CATALOG.md). Ejecuta el notebook con este directorio como carpeta de trabajo.


## Trayectoria de caja y deuda por proyecto

`python/src/risk_models.py::project_cash_path` integra CFADS periódico, servicio
de deuda, caja inicial y piso de liquidez. Devuelve la trayectoria sin
financiamiento automático, primer período bajo el piso (0 si ya se incumple
al inicio), aporte mínimo para sostenerlo y DSCR por período. La igualdad al
piso no es incumplimiento; servicio cero produce DSCR indefinido. Supone
flujos al cierre de cada período y no modela intereses de financiación,
impuestos ni distribución de caja. Es un ejercicio determinístico con
escenarios aportados por el usuario, no una calibración de obra ni pronóstico.

```bash
python3 -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab/04-modelos-compartidos/python/tests -p 'test_*.py'
```

El [ejercicio ICOCED](examples/icoced_cash_path/README.md) aplica 34 ventanas de costos DANE a caja y deuda hipotéticas, usando este mismo cálculo de trayectoria.
