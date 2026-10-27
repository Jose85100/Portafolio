# MVP

- Qué: selector de umbral de caja para solicitar una facilidad con demora fija, un giro y costo explícito.
- Corre: `bash run.sh`; entorno preparado `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- Produce: tabla de umbrales, trayectorias de caja/deuda, sensibilidad de demora, stress fuera del diseño, JSON, figura y notebook ejecutado.
- No cubre: revocación, amortización, líneas múltiples, probabilidades calibradas, costos de compromiso, contabilidad completa y operación productiva.
- Decisión: solicitar al observar caja≤6 bajo supuestos; ajustar buffer/monto/lead si cambian; rediseñar cuando menú factible es vacío.
- Madurez: componente S2 sintético, no equivalencia automática M2; programa18 conserva S1.
- Negativos: costo extra por anticipación, fracaso fuera de escenarios y falta de factibilidad con lead4.
- Checklist: src✓ comando✓ tests✓ baseline✓ salida/figura✓ notebookoutputs✓5refs✓ informe14p✓ README/MVP/entorno✓ carpeta18✓ madurezlocal✓. Revisión y publicación separadas; no merge automático.
