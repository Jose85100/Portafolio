# MVP
- Qué: banda inferior/superior de primera ruptura con intervalos de transición y búsqueda de reserva en41puntos.
- Corre: `bash run.sh`, Python3.12. Mantener hermano markov-first-breach-audit para baselineforwardDP.
- Salidas: código tipado, tests, cobertura/lint/tipos, curvasCSV, métricasJSON, figura y notebook ejecutado.
- No cubre: estimación de intervalos, cobertura probabilística, una única matriz fija adversarial, reacción de clientes, líneas de fondeo, incertidumbre de flujos o validación real.
- Convención: flujo antes de transición; caja<0 rompe y cero sobrevive. Horizonte≤40,caja0..100 para cerrar alcance.
- Estado: componente prototipo sintético, no certificación operacional ni de todo el programa.
- Entorno: dependencias directas fijadas yvenv, no lock completo de transitivas.
