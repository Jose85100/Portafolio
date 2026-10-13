# Financial & Construction Risk Lab

**Estado:** laboratorio en construcción. Los documentos son especificaciones de investigación; el código incluido es un prototipo cuantitativo reproducible, **no un modelo validado para decisiones de inversión o crédito**.

## Propósito
Desarrollar modelos auditables de riesgo financiero corporativo y riesgo integral de constructoras, desde la identificación de exposiciones hasta la cuantificación probabilística, stress testing, validación independiente y gobierno.

## Líneas
- **01-corporate-financial-risk:** liquidez, tasas y FX.
- **02-construction-enterprise-risk:** caja de obra, plazos, costos, preventas, contratistas y covenants.
- **03-research-in-progress:** gemelos digitales y contagio macro-inmobiliario.

## Estándar mínimo de cada proyecto
Definición de evento de riesgo y horizonte; variables y fuentes; ecuaciones y supuestos; estrategia de estimación y dependencias; simulación y pruebas de estrés; backtesting/calibración; controles de leakage y sesgo; límites de uso y plan de validación independiente.

## Implementación inicial
El prototipo de `02-construction-enterprise-risk/01-project-cashflow-at-risk/src/model.py` simula escenarios mensuales con una semilla reproducible. Ejecutar desde la raíz del repositorio:

```bash
python -m unittest discover -s 03-financial-risk/07-financial-and-construction-risk-lab/02-construction-enterprise-risk/01-project-cashflow-at-risk/tests -p 'test_*.py' -v
```

**No hay datos reales ni parámetros calibrados.** El motor sirve como base verificable, no como prueba de desempeño predictivo.
