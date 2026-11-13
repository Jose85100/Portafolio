# MVP
- Qué: DP de primera ruptura de caja con estados de régimen y absorción de probabilidad, más comparación terminal y búsqueda de reserva mínima en rejilla.
- Cómo: `bash run.sh`, Python3.12. `SKIP_INSTALL=1` reutiliza entorno listo.
- Salidas: src tipado, tests propios/integración, evidencia de cobertura/lint/tipos,60ensayosMC,82reservas evaluadas,40masas de primera ruptura, CSV/JSON/figura y notebook ejecutado.
- No cubre: estimación de parámetros, LCR/NSFR, crédito de emergencia, liquidación endógena, colateral, múltiples monedas, incertidumbre de matriz o validación con datos reales.
- Convención: flujo del día utiliza régimen actual y después transiciona; caja<0 rompe, caja0 no. Absorción mide el evento histórico; no impone política de liquidación.
- Madurez: prototipo sintético de componente; ningún programa entero se eleva aM2/M3.
- Entorno: versiones directas fijadas y venv; transitivas sin bloqueo completo. Requiere laboratorio vecino solo para la suite de integración.
