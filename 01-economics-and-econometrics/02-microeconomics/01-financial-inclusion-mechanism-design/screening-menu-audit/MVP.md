# MVP: núcleo estático de screening IC/IR

- Qué es: solución analítica y numérica de contratos para dos tipos privados, utilidad cuasilineal y coste cuadrático.
- Cómo corre: `bash run.sh`, con Python 3.11+, venv y PyPI.
- Produce: 81 escenarios con contratos, restricciones y baseline óptimo; comparación QP, sensibilidad, figura, costes, tests y notebook ejecutado.
- Hipótesis previa: beneficio del menú estricto en el ejemplo ≥1,2 veces mejor contrato único; slacks ≥−1e−8; error de beneficio QP ≤1e−7 en la grilla. Resultado ancla 0,6249988 frente a 0,5.
- Qué no cubre: datos de originación, default, tipos estimados, flujo contingente, moral hazard ni validación causal.
- Madurez: S2 local del componente; pregunta principal del programa sigue en formulación. No equivalente a M2 ni operacional.
