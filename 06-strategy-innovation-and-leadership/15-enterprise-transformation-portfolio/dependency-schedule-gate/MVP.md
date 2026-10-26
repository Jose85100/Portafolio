# MVP

- Qué: calendarizador exacto pequeño para inversiones opcionales con precedencias de terminación, caja por período y capacidad.
- Corre: `bash run.sh`; entorno preparado `REUSE_ENV=1 PYTHON=/ruta/python bash run.sh`.
- Produce: calendarios CSV, sensibilidad horizonte/capacidad/valor habilitador, JSON, figura y notebook ejecutado.
- No cubre: incertidumbre, replanificación, preemption, cobros múltiples, caja acumulada, contratación y aplicaciones empresariales validadas.
- Madurez: componente S2 sintético; no equivalente automático a M2, programa15 no recertificado.
- Decisión: continuar con calendario factible y NPVpositivo; ajustar cuando cambien duración/caja/dependencias; detener si toda selección tiene NPV≤0.
- Evidencia negativa: exacto empata greedy en configuración inicial; incremento+.5no demostrado allí.
- Checklist: src✓ comando✓ tests✓ baseline✓ salidas/figura✓ notebookoutputs✓5referencias✓ informe/README/MVP/entorno✓ carpeta15✓ madurez✓. Revisión independiente y publicación se registran separadamente; no merge automático.
