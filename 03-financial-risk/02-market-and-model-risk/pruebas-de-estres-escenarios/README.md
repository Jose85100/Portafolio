# Pruebas de estrés: laboratorio y aplicación observada

El laboratorio controlado demuestra estrés multifactor y estrés inverso cuando se conocen las sensibilidades y los escenarios. La aplicación con datos oficiales añade un contraste observado para riesgo de tasa.

## Aplicación oficial: choques diarios de tasa

Con la serie del U.S. Treasury de 2024-01-02 a 2026-11-10, el mayor aumento diario del rendimiento a 10 años fue 19 pb, equivalente a una pérdida lineal de USD 152.000 (1,52%) sobre USD 10 millones con duración fija de ocho años. El estrés inverso de 10% requiere 125 pb en un día; no ocurrió en esta muestra.

Es una aplicación observada de un factor. La curva a plazo constante no mide un bono concreto; la aproximación omite convexidad, carry, roll-down y escenarios conjuntos. La ausencia de un choque tan grande en 2024–2026 no permite descartarlo.

- [Informe y límites de la aplicación](reports/official-application-2026-11-10.md)
- [Runner reproducible](official_application.py)
- [Resultados observados](data/official/stress_summary.json)
- [Figura de choques históricos](reports/figures/treasury-historical-stress.png)
- [Datos oficiales y semántica](../var-es-tres-metodos/data/README.md)

Para reproducir desde la raíz de este proyecto:

```bash
MPLCONFIGDIR=/tmp/mplconfig MPLBACKEND=Agg python3 official_application.py
```

## Laboratorio controlado multifactor

Escenarios con sensibilidades lineales para acciones, tasas, USD/COP y spreads muestran cómo se agregan contribuciones y cómo se resuelve un estrés inverso bajo esos supuestos. El escenario de crisis y sus sensibilidades sirven para estudiar la mecánica; esta edición no los presenta como una reconstrucción histórica.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
acciones  tasa_10y_pb  usd_cop  spread_credito_pb  total_pct    perdida
crisis_2008         -17.10         0.74     3.00              -0.84     -14.20 -1419600.0
alza_de_tasas        -5.40        -1.55     0.96              -0.25      -6.24  -624200.0
choque_cambiario     -4.05        -0.37     3.60              -0.19      -1.01  -101100.0
recesion_local       -9.90         0.50     1.80              -0.52      -8.13  -812900.0
Peor escenario: crisis_2008 (-14.20% | -1,419,600)
Estres inverso: para perder 10.0% solo con acciones se requiere un choque de -22.2%
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
