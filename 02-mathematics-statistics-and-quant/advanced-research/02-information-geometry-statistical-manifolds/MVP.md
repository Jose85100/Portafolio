# MVP del programa 02 — detección de cambios y geometría de información

Qué es: detector continuo univariado por proyección gaussiana Fisher–Rao, comparado con KS y Wasserstein-1 bajo referencia fija y calibración separada. La auditoría categórica previa se conserva como componente auxiliar.

Cómo se corre: Python 3.12, make, venv y PyPI; ejecutar `make run` desde esta carpeta. El comando reproduce ambos estudios, pruebas, informes, CSV/JSON/NPZ, figuras y notebooks con outputs.

Qué produce el estudio principal: 798 scores de calibración (399 por tamaño), 3.000 ventanas de evaluación, 9.000 decisiones, 30 tasas con Wilson 95%, umbrales, referencia de 80 dígitos y vistas previas de muestras con semillas completas. El piloto desfavorable de calibración marginal queda guardado. API en src/drift.py, experimento en experiments/drift.json, informe.md y drift_notebook.ipynb.

Qué produce el anexo: 1.600 pares categóricos, 6.400 p-valores, 75 tiempos, 12 oráculos y 132 puntos geodésicos. docs/categorical-audit.md y notebook.ipynb conservan su interpretación.

Qué NO cubre: control secuencial, alarma conjunta de los tres métodos, calibración por bloques, datos bancarios, validación económica, superioridad universal o detección de cualquier cambio con una proyección de dos momentos. Las ventanas AR1 violan la ley de calibración y se muestran como fallo.

Garantía acotada: bajo ventanas limpias independientes de igual ley, el rango binomial controla con confianza 1-delta la probabilidad de falsa alarma por ventana de cada detector. Una tasa observada en 300 ventanas puede exceder alpha; no se afirma que cada calibración ni cada simulación cumpla exactamente el objetivo.

Estado: S2 acotado. Se resolvieron los conflictos con main conservando el programa 05. Tests del código nuevo y anterior, numerical-core, lint y tipos se incluyen en make run. Figuras revisadas por separado; inspección visual integral de ambos notebooks en visor pendiente.
